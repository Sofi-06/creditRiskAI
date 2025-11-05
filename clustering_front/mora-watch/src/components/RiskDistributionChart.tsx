import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { Applicant } from "@/lib/mockData";

interface RiskDistributionChartProps {
  applicants: Applicant[];
}

export function RiskDistributionChart({ applicants }: RiskDistributionChartProps) {
  const riskCounts = applicants.reduce((acc, app) => {
    acc[app.riskLevel] = (acc[app.riskLevel] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const data = [
    { name: "Bajo", value: riskCounts["Bajo"] || 0, color: "hsl(var(--chart-2))" },
    { name: "Medio", value: riskCounts["Medio"] || 0, color: "hsl(var(--chart-3))" },
    { name: "Alto", value: riskCounts["Alto"] || 0, color: "hsl(var(--chart-4))" },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución de Riesgo</CardTitle>
        <CardDescription>Clasificación de solicitantes por nivel de riesgo</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
