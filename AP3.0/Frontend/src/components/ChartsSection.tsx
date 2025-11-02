import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartsSectionProps {
  data: any;
}

const ChartsSection = ({ data }: ChartsSectionProps) => {
  // Transform data for charts
  const barChartData = Object.entries(data.sectors || {}).map(([sector, schemes]: [string, any]) => {
    const schemesList = Array.isArray(schemes) ? schemes : [];
    const avgPercentage = schemesList.length > 0 
      ? schemesList.reduce((sum: number, s: any) => sum + (s.percentage || 0), 0) / schemesList.length 
      : 0;
    return {
      sector,
      achievement: avgPercentage.toFixed(1),
      target: 100,
    };
  });

  const pieChartData = Object.entries(data.sectors || {}).map(([sector, schemes]: [string, any]) => {
    const schemesList = Array.isArray(schemes) ? schemes : [];
    return {
      name: sector,
      value: schemesList.length,
    };
  });

  const COLORS = ['hsl(var(--primary))', 'hsl(var(--accent))', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Bar Chart - Achievement by Sector */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Achievement by Sector (%)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="sector" 
                tick={{ fill: 'hsl(var(--foreground))' }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fill: 'hsl(var(--foreground))' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem'
                }}
              />
              <Legend />
              <Bar dataKey="achievement" fill="hsl(var(--primary))" name="Achievement %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Pie Chart - Schemes Distribution */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Schemes Distribution by Sector</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="hsl(var(--primary))"
                dataKey="value"
              >
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChartsSection;
