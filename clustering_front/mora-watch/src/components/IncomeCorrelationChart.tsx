import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Applicant } from "@/lib/mockData";

interface IncomeCorrelationChartProps {
  applicants: Applicant[];
}

export function IncomeCorrelationChart({ applicants }: IncomeCorrelationChartProps) {
  const data = applicants.map(app => ({
    income: app.income,
    defaultProb: app.defaultProbability * 100,
    name: app.name
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ingresos vs Probabilidad de Mora</CardTitle>
        <CardDescription>Correlación entre nivel de ingresos y riesgo de impago</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              dataKey="income" 
              name="Ingresos" 
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <YAxis 
              type="number" 
              dataKey="defaultProb" 
              name="Prob. Mora" 
              tickFormatter={(value) => `${value.toFixed(0)}%`}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              formatter={(value: number, name: string) => {
                if (name === "Ingresos") return `$${value.toLocaleString()}`;
                if (name === "Prob. Mora") return `${value.toFixed(1)}%`;
                return value;
              }}
            />
            <Scatter data={data} fill="hsl(var(--chart-1))" />
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
