import { useEffect, useState } from "react";
import { ServiceHealth } from "@/components/admin/ServiceHealth";
import { KafkaMetrics } from "@/components/admin/KafkaMetrics";
import { SystemMetrics } from "@/components/admin/SystemMetrics";
import {
  Card,
  Title,
  Text,
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Grid,
  Metric,
  Flex,
  ProgressBar,
  Badge,
} from "@tremor/react";

interface DashboardData {
  service_health: Record<
    string,
    {
      status: string;
      last_check: string;
      last_successful_check: string;
      response_time: number;
      error_message: string | null;
      topics?: number;
    }
  >;
  service_metrics: {
    kafka: {
      broker_count: number;
      topic_count: number;
      partition_count: number;
    };
  };
  timestamp: string;
}

interface SystemMetricsData {
  gc_stats: {
    collected: Record<string, number>;
    uncollectable: Record<string, number>;
    collections: Record<string, number>;
  };
  memory: {
    virtual: number;
    resident: number;
  };
  python_info: {
    version: string;
    implementation: string;
  };
  process: {
    cpu_seconds: number;
    open_fds: number;
    max_fds: number;
  };
  django: {
    db_connections: number;
    db_queries: number;
    requests_total: number;
    response_time_avg: number;
  };
}

const parsePrometheusMetrics = (metricsText: string): SystemMetricsData => {
  const metrics = {
    gc_stats: {
      collected: {} as Record<string, number>,
      uncollectable: {} as Record<string, number>,
      collections: {} as Record<string, number>,
    },
    memory: {
      virtual: 0,
      resident: 0,
    },
    python_info: {
      version: "",
      implementation: "",
    },
    process: {
      cpu_seconds: 0,
      open_fds: 0,
      max_fds: 0,
    },
    django: {
      db_connections: 0,
      db_queries: 0,
      requests_total: 0,
      response_time_avg: 0,
    },
  };

  const lines = metricsText.split("\n");

  lines.forEach((line) => {
    if (line.startsWith("#")) return;

    const match = line.match(/^([^{]+)({[^}]+})?\s+(.+)/);
    if (!match) return;

    const [, name, labels, value] = match;

    let count: number;

    switch (name) {
      case "python_gc_objects_collected_total":
        if (labels) {
          const gen = labels.match(/generation="(\d+)"/)?.[1];
          if (gen) metrics.gc_stats.collected[gen] = parseFloat(value);
        }
        break;
      case "python_gc_collections_total":
        if (labels) {
          const gen = labels.match(/generation="(\d+)"/)?.[1];
          if (gen) metrics.gc_stats.collections[gen] = parseFloat(value);
        }
        break;
      case "process_virtual_memory_bytes":
        metrics.memory.virtual = parseFloat(value);
        break;
      case "process_resident_memory_bytes":
        metrics.memory.resident = parseFloat(value);
        break;
      case "process_cpu_seconds_total":
        metrics.process.cpu_seconds = parseFloat(value);
        break;
      case "process_open_fds":
        metrics.process.open_fds = parseFloat(value);
        break;
      case "process_max_fds":
        metrics.process.max_fds = parseFloat(value);
        break;
      case "django_db_execute_total":
        if (labels?.includes('alias="default"')) {
          metrics.django.db_queries = parseFloat(value);
        }
        break;
      case "django_http_requests_total_by_method_total":
        if (labels?.includes('method="GET"')) {
          metrics.django.requests_total = parseFloat(value);
        }
        break;
      case "django_http_requests_latency_including_middlewares_seconds_sum":
        count = parseFloat(
          lines
            .find((l) =>
              l.startsWith(
                "django_http_requests_latency_including_middlewares_seconds_count"
              )
            )
            ?.split(" ")[1] || "0"
        );
        if (count > 0) {
          metrics.django.response_time_avg = (parseFloat(value) / count) * 1000; // Convert to ms
        }
        break;
      case "python_info":
        if (labels) {
          metrics.python_info.implementation =
            labels.match(/implementation="([^"]+)"/)?.[1] || "";
          const major = labels.match(/major="([^"]+)"/)?.[1] || "";
          const minor = labels.match(/minor="([^"]+)"/)?.[1] || "";
          const patch = labels.match(/patchlevel="([^"]+)"/)?.[1] || "";
          metrics.python_info.version = `${major}.${minor}.${patch}`;
        }
        break;
    }
  });

  return metrics;
};

export default function AdminDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [systemMetrics, setSystemMetrics] = useState<SystemMetricsData | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashboardResponse, metricsResponse] = await Promise.all([
          fetch("http://54.208.64.57:8002/api/admin/dashboard/"),
          fetch("http://54.208.64.57:8002/metrics"),
        ]);

        if (!dashboardResponse.ok || !metricsResponse.ok) {
          throw new Error("Failed to fetch data");
        }

        const dashboardJson = await dashboardResponse.json();
        const metricsText = await metricsResponse.text();
        const parsedMetrics = parsePrometheusMetrics(metricsText);

        setDashboardData(dashboardJson);
        setSystemMetrics(parsedMetrics);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    const interval = setInterval(fetchData, 30000);
    fetchData();

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <Card className="w-full max-w-lg">
          <Flex justifyContent="center" className="space-x-2">
            <Title>Loading dashboard</Title>
            <ProgressBar value={75} color="blue" />
          </Flex>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <Card className="w-full max-w-lg bg-red-50">
          <Flex justifyContent="center" className="space-x-2">
            <Title color="red">Error</Title>
            <Text color="red">{error}</Text>
          </Flex>
        </Card>
      </div>
    );
  }

  if (!dashboardData || !systemMetrics) {
    return null;
  }

  const healthyServices = Object.values(dashboardData.service_health).filter(
    (service) => service.status === "healthy"
  ).length;
  const totalServices = Object.keys(dashboardData.service_health).length;
  const healthPercentage = (healthyServices / totalServices) * 100;

  return (
    <main className="p-6 bg-gray-50 min-h-screen">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <Flex justifyContent="between" alignItems="center">
            <div>
              <Flex alignItems="center" className="space-x-2">
                <Title>System Dashboard</Title>
                <Badge size="xl" color="gray">
                  Admin
                </Badge>
              </Flex>
              <Text className="mt-2">
                Last updated:{" "}
                {new Date(dashboardData.timestamp).toLocaleString()}
              </Text>
            </div>
            <Card
              className="max-w-xs"
              decoration="top"
              decorationColor={healthPercentage === 100 ? "emerald" : "orange"}
            >
              <Flex justifyContent="between" alignItems="center">
                <div>
                  <Text>System Health</Text>
                  <Metric>{healthPercentage.toFixed(1)}%</Metric>
                </div>
                <Badge
                  size="xl"
                  color={healthPercentage === 100 ? "emerald" : "orange"}
                >
                  {healthyServices} / {totalServices}
                </Badge>
              </Flex>
              <ProgressBar
                value={healthPercentage}
                color={healthPercentage === 100 ? "emerald" : "orange"}
                className="mt-3"
              />
            </Card>
          </Flex>
        </div>

        {/* Main Content */}
        <TabGroup>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>System Metrics</Tab>
            <Tab>Service Health</Tab>
            <Tab>Kafka</Tab>
          </TabList>
          <TabPanels>
            <TabPanel>
              <div className="mt-6">
                <Grid numItems={1} numItemsLg={2} className="gap-6">
                  <div>
                    <Card>
                      <Title>Service Health Overview</Title>
                      <ServiceHealth
                        healthData={dashboardData.service_health}
                      />
                    </Card>
                  </div>
                  <div>
                    <Card>
                      <Title>System Overview</Title>
                      <SystemMetrics metricsData={systemMetrics} />
                    </Card>
                  </div>
                </Grid>
              </div>
            </TabPanel>
            <TabPanel>
              <div className="mt-6">
                <SystemMetrics metricsData={systemMetrics} />
              </div>
            </TabPanel>
            <TabPanel>
              <div className="mt-6">
                <ServiceHealth healthData={dashboardData.service_health} />
              </div>
            </TabPanel>
            <TabPanel>
              <div className="mt-6">
                <KafkaMetrics metrics={dashboardData.service_metrics.kafka} />
              </div>
            </TabPanel>
          </TabPanels>
        </TabGroup>
      </div>
    </main>
  );
}
