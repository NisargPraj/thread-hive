import {
  Card,
  Text,
  Metric,
  Flex,
  Grid,
  Title,
  DonutChart,
  Legend,
  ProgressBar,
  Badge,
  BarChart,
} from "@tremor/react";

interface KafkaMetricsProps {
  metrics: {
    broker_count: number;
    topic_count: number;
    partition_count: number;
  };
}

export function KafkaMetrics({ metrics }: KafkaMetricsProps) {
  const chartData = [
    {
      name: "Brokers",
      value: metrics.broker_count,
    },
    {
      name: "Topics",
      value: metrics.topic_count,
    },
    {
      name: "Partitions",
      value: metrics.partition_count,
    },
  ];

  const barChartData = [
    {
      name: "Distribution",
      Brokers: metrics.broker_count,
      Topics: metrics.topic_count,
      Partitions: metrics.partition_count,
    },
  ];

  const valueFormatter = (number: number) => {
    return `${number}`;
  };

  // Calculate utilization percentage (example metric)
  const utilizationPercentage =
    (metrics.topic_count / metrics.partition_count) * 100;

  return (
    <div className="space-y-6">
      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        <Card
          decoration="top"
          decorationColor="indigo"
          className="hover:border-indigo-200 transition-colors"
        >
          <Flex alignItems="start">
            <div>
              <Text>Active Brokers</Text>
              <Metric>{metrics.broker_count}</Metric>
            </div>
            <Badge color="indigo" size="xl">
              Online
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="text-sm text-gray-500">Broker Status</Text>
            <Text className="text-sm text-indigo-500">100% Available</Text>
          </Flex>
        </Card>

        <Card
          decoration="top"
          decorationColor="emerald"
          className="hover:border-emerald-200 transition-colors"
        >
          <Flex alignItems="start">
            <div>
              <Text>Total Topics</Text>
              <Metric>{metrics.topic_count}</Metric>
            </div>
            <Badge color="emerald" size="xl">
              Active
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="text-sm text-gray-500">Topic Health</Text>
            <Text className="text-sm text-emerald-500">Healthy</Text>
          </Flex>
        </Card>

        <Card
          decoration="top"
          decorationColor="orange"
          className="hover:border-orange-200 transition-colors"
        >
          <Flex alignItems="start">
            <div>
              <Text>Total Partitions</Text>
              <Metric>{metrics.partition_count}</Metric>
            </div>
            <Badge color="orange" size="xl">
              Distributed
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="text-sm text-gray-500">Distribution</Text>
            <Text className="text-sm text-orange-500">Balanced</Text>
          </Flex>
        </Card>
      </Grid>

      <Card>
        <Title>Resource Distribution</Title>
        <Text className="mt-2">Overview of Kafka cluster resources</Text>
        <Flex className="mt-6" justifyContent="center">
          <DonutChart
            data={chartData}
            category="value"
            index="name"
            valueFormatter={valueFormatter}
            colors={["indigo", "emerald", "orange"]}
            className="h-52"
            showAnimation={true}
          />
        </Flex>
        <Legend
          className="mt-6"
          categories={["Brokers", "Topics", "Partitions"]}
          colors={["indigo", "emerald", "orange"]}
        />
      </Card>

      <Card>
        <Title>Cluster Metrics</Title>
        <Text className="mt-2">Detailed view of cluster components</Text>
        <BarChart
          className="mt-6 h-48"
          data={barChartData}
          index="name"
          categories={["Brokers", "Topics", "Partitions"]}
          colors={["indigo", "emerald", "orange"]}
          showLegend={false}
          showAnimation={true}
          valueFormatter={valueFormatter}
        />
      </Card>

      <Card>
        <Title>Cluster Utilization</Title>
        <Metric className="mt-2">{utilizationPercentage.toFixed(1)}%</Metric>
        <Flex className="mt-4">
          <Text className="truncate">Topics per Partition Ratio</Text>
          <Text>{utilizationPercentage.toFixed(0)}%</Text>
        </Flex>
        <ProgressBar
          value={utilizationPercentage}
          color="indigo"
          className="mt-2"
        />
      </Card>
    </div>
  );
}
