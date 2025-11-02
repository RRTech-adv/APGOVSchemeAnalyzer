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
          <ResponsiveContainer width="100%" height={450}>
            <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 10, bottom: 150 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="sector" 
                tick={{ 
                  fill: 'hsl(var(--foreground))',
                  fontSize: 10,
                  angle: -60,
                  textAnchor: 'end',
                  dy: 5,
                  dx: -5
                }}
                interval={0}
                height={150}
                tickFormatter={(value) => {
                  // Truncate long sector names more aggressively
                  const maxLength = 25;
                  if (value.length > maxLength) {
                    return value.substring(0, maxLength) + '...';
                  }
                  return value;
                }}
              />
              <YAxis 
                tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
                width={60}
                label={{ value: 'Achievement %', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                  maxWidth: '300px',
                  wordWrap: 'break-word'
                }}
                labelFormatter={(label) => (
                  <div style={{ marginBottom: '4px', fontWeight: 'bold', wordBreak: 'break-word' }}>
                    {label}
                  </div>
                )}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
              />
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
          <ResponsiveContainer width="100%" height={450}>
            <PieChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <Pie
                data={pieChartData}
                cx="50%"
                cy="45%"
                labelLine={true}
                label={({ name, percent }) => {
                  // Show only percentage on pie, full name in tooltip
                  return `${(percent * 100).toFixed(0)}%`;
                }}
                outerRadius={100}
                fill="hsl(var(--primary))"
                dataKey="value"
                labelStyle={{ 
                  fontSize: '11px',
                  fill: 'hsl(var(--foreground))',
                  fontWeight: 'bold'
                }}
              >
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number, name: string) => [
                  `${value} scheme${value !== 1 ? 's' : ''}`,
                  name
                ]}
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                  maxWidth: '300px',
                  wordWrap: 'break-word'
                }}
                labelStyle={{ fontWeight: 'bold', marginBottom: '4px' }}
              />
              <Legend 
                verticalAlign="bottom"
                height={80}
                wrapperStyle={{ fontSize: '11px', paddingTop: '20px' }}
                formatter={(value: string) => {
                  // Show full names in legend with wrapping
                  return value;
                }}
                iconType="circle"
                layout="horizontal"
              />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChartsSection;
