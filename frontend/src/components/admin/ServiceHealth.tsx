import type { Color } from "@tremor/react";
import {
  Card,
  Text,
  Metric,
  Flex,
  BadgeDelta,
  Grid,
  AreaChart,
  Title,
  Badge,
} from "@tremor/react";

interface HealthData {
  status: string;
  last_check: string;
  last_successful_check: string;
  response_time: number;
  error_message: string | null;
  topics?: number;
}

interface ServiceHealthProps {
  healthData: Record<string, HealthData>;
}

const getStatusColor = (status: string): Color => {
  return status === "healthy" ? "emerald" : "red";
};

const getStatusIcon = (status: string) => {
  return status === "healthy" ? "✓" : "✗";
};

export function ServiceHealth({ healthData }: ServiceHealthProps) {
  // Create data for response time chart
  const chartData = Object.entries(healthData).map(([service, data]) => ({
    name: service,
    "Response Time": data.response_time,
    Status: data.status,
  }));

  // Calculate average response time
  const avgResponseTime =
    Object.values(healthData).reduce(
      (acc, curr) => acc + curr.response_time,
      0
    ) / Object.keys(healthData).length;

  return (
    <div className="space-y-6">
      {/* Summary Metrics */}
      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6 mt-6">
        {Object.entries(healthData).map(([service, data]) => (
          <Card
            key={service}
            decoration="left"
            decorationColor={getStatusColor(data.status)}
          >
            <Flex alignItems="start">
              <div className="w-full">
                <Flex>
                  <Text className="capitalize truncate">{service}</Text>
                  <Badge
                    color={getStatusColor(data.status)}
                    size="xs"
                    icon={() => (
                      <span className="text-xs">
                        {getStatusIcon(data.status)}
                      </span>
                    )}
                  >
                    {data.status}
                  </Badge>
                </Flex>
                <Metric className="mt-2">
                  {data.response_time.toFixed(2)}ms
                </Metric>
                <Flex className="mt-4 space-x-2">
                  <Text className="text-sm text-gray-500">Last Check:</Text>
                  <Text className="text-sm truncate">
                    {new Date(data.last_check).toLocaleTimeString()}
                  </Text>
                </Flex>
                {data.topics && (
                  <Flex className="mt-2 space-x-2">
                    <Text className="text-sm text-gray-500">Topics:</Text>
                    <Badge size="xs" color="blue">
                      {data.topics}
                    </Badge>
                  </Flex>
                )}
                {data.error_message && (
                  <Text className="mt-2 text-sm text-red-500">
                    {data.error_message}
                  </Text>
                )}
              </div>
              <BadgeDelta
                deltaType={
                  data.response_time < avgResponseTime
                    ? "moderateDecrease"
                    : "moderateIncrease"
                }
              >
                {data.response_time < avgResponseTime ? "Below" : "Above"} Avg
              </BadgeDelta>
            </Flex>
          </Card>
        ))}
      </Grid>

      {/* Response Time Chart */}
      <Card>
        <Title>Response Time Trends</Title>
        <Text className="mt-2">Service response times comparison</Text>
        <AreaChart
          className="mt-6 h-72"
          data={chartData}
          index="name"
          categories={["Response Time"]}
          colors={["blue"]}
          showLegend={false}
          showGridLines={true}
          showAnimation={true}
          valueFormatter={(value) => `${value.toFixed(2)}ms`}
          showYAxis={true}
          showXAxis={true}
        />
      </Card>
    </div>
  );
}
