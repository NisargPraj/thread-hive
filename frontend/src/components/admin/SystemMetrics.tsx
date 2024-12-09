import {
  Card,
  Text,
  Metric,
  Flex,
  Grid,
  Title,
  ProgressBar,
  Badge,
} from "@tremor/react";

interface MetricsData {
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

interface SystemMetricsProps {
  metricsData: MetricsData;
}

const formatBytes = (bytes: number): string => {
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }
  return `${value.toFixed(2)} ${units[unitIndex]}`;
};

export function SystemMetrics({ metricsData }: SystemMetricsProps) {
  const memoryUsagePercent =
    (metricsData.memory.resident / metricsData.memory.virtual) * 100;
  const fdsUsagePercent =
    (metricsData.process.open_fds / metricsData.process.max_fds) * 100;

  return (
    <div className="space-y-6">
      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        {/* Memory Usage Card */}
        <Card decoration="top" decorationColor="blue">
          <Flex alignItems="start">
            <div>
              <Text>Memory Usage</Text>
              <Metric>{formatBytes(metricsData.memory.resident)}</Metric>
            </div>
            <Badge color="blue" size="xl">
              Memory
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="truncate">Virtual Memory Usage</Text>
            <Text>{memoryUsagePercent.toFixed(1)}%</Text>
          </Flex>
          <ProgressBar
            value={memoryUsagePercent}
            color="blue"
            className="mt-2"
          />
        </Card>

        {/* CPU Usage Card */}
        <Card decoration="top" decorationColor="emerald">
          <Flex alignItems="start">
            <div>
              <Text>CPU Time</Text>
              <Metric>{metricsData.process.cpu_seconds.toFixed(2)}s</Metric>
            </div>
            <Badge color="emerald" size="xl">
              CPU
            </Badge>
          </Flex>
          <Text className="mt-4 text-sm text-gray-500">
            Total CPU time consumed
          </Text>
        </Card>

        {/* File Descriptors Card */}
        <Card decoration="top" decorationColor="orange">
          <Flex alignItems="start">
            <div>
              <Text>Open File Descriptors</Text>
              <Metric>{metricsData.process.open_fds}</Metric>
            </div>
            <Badge color="orange" size="xl">
              FDs
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="truncate">FDs Usage</Text>
            <Text>{fdsUsagePercent.toFixed(1)}%</Text>
          </Flex>
          <ProgressBar
            value={fdsUsagePercent}
            color="orange"
            className="mt-2"
          />
        </Card>
      </Grid>

      {/* Python Runtime Info */}
      <Card>
        <Title>Runtime Information</Title>
        <Grid numItems={1} numItemsSm={2} className="gap-6 mt-4">
          <div>
            <Text>Python Version</Text>
            <Metric>{metricsData.python_info.version}</Metric>
            <Text className="text-sm text-gray-500 mt-2">
              Implementation: {metricsData.python_info.implementation}
            </Text>
          </div>
          <div>
            <Text>Database Stats</Text>
            <Metric>{metricsData.django.db_queries}</Metric>
            <Text className="text-sm text-gray-500 mt-2">
              Total Queries Executed
            </Text>
          </div>
        </Grid>
      </Card>

      {/* Garbage Collection Stats */}
      <Card>
        <Title>Garbage Collection Statistics</Title>
        <div className="mt-4">
          <Grid numItems={1} numItemsSm={3} className="gap-4">
            {Object.entries(metricsData.gc_stats.collected).map(
              ([gen, count]) => (
                <Card key={gen}>
                  <Text>Generation {gen}</Text>
                  <Metric>{count}</Metric>
                  <Text className="text-sm text-gray-500 mt-2">
                    Collections: {metricsData.gc_stats.collections[gen]}
                  </Text>
                </Card>
              )
            )}
          </Grid>
        </div>
      </Card>

      {/* Request Statistics */}
      <Card>
        <Title>Request Statistics</Title>
        <div className="mt-4">
          <Grid numItems={1} numItemsSm={2} className="gap-6">
            <div>
              <Text>Total Requests</Text>
              <Metric>{metricsData.django.requests_total}</Metric>
            </div>
            <div>
              <Text>Average Response Time</Text>
              <Metric>
                {metricsData.django.response_time_avg.toFixed(2)}ms
              </Metric>
            </div>
          </Grid>
        </div>
      </Card>
    </div>
  );
}
