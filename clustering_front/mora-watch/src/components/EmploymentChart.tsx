import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Applicant } from "@/lib/mockData";

interface EmploymentChartProps {
  applicants: Applicant[];
}

export function EmploymentChart({ applicants }: EmploymentChartProps) {
  const employmentData = applicants.reduce((acc, app) => {
    const existing = acc.find(item => item.status === app.employmentStatus);
    if (existing) {
      existing.count++;
      existing.avgDefault = (existing.avgDefault * (existing.count - 1) + app.defaultProbability) / existing.count;
    } else {
      acc.push({
        status: app.employmentStatus,
        count: 1,
        avgDefault: app.defaultProbability
      });
    }
    return acc;
  }, [] as Array<{ status: string; count: number; avgDefault: number }>);

  const data = employmentData.map(item => ({
    name: item.status,
    probability: (item.avgDefault * 100).toFixed(1)
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Probabilidad de Mora por Estado Laboral</CardTitle>
        <CardDescription>Promedio de riesgo según situación de empleo</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => `${value}%`} />
            <Tooltip 
              formatter={(value: number) => `${value}%`}
              labelFormatter={(label) => `Estado: ${label}`}
            />
            <Bar dataKey="probability" fill="hsl(var(--chart-1))" name="Prob. Mora" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
