import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Scheme {
  name: string;
  target?: number;
  achievement?: number;
  percentage: number;
  achievement_percentage?: number;
  current_status?: string;
  data_source?: string;
  remarks?: string;
}

interface SectorCardProps {
  title: string;
  schemes: Scheme[];
  icon: React.ReactNode;
}

const SectorCard = ({ title, schemes, icon }: SectorCardProps) => {
  const avgPercentage = schemes.length > 0 
    ? schemes.reduce((sum, s) => sum + (s.percentage || s.achievement_percentage || 0), 0) / schemes.length 
    : 0;
  
  const getTrendIcon = (percentage: number) => {
    if (percentage >= 90) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (percentage >= 70) return <Minus className="h-4 w-4 text-yellow-600" />;
    return <TrendingDown className="h-4 w-4 text-red-600" />;
  };

  const getStatusColor = (percentage: number) => {
    if (percentage >= 90) return "bg-green-100 text-green-800 border-green-200";
    if (percentage >= 70) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  return (
    <Card className="hover:shadow-elevated transition-smooth">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {icon}
            <span>{title}</span>
          </div>
          <Badge variant="outline" className={getStatusColor(avgPercentage)}>
            {avgPercentage.toFixed(1)}%
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {schemes.map((scheme, index) => (
            <div key={index} className="border-l-2 border-primary/30 pl-4 py-2 hover:border-primary transition-smooth">
              <div className="flex items-start justify-between mb-1">
                <p className="text-sm font-medium text-foreground">{scheme.name}</p>
                <div className="flex items-center space-x-1">
                  {getTrendIcon(scheme.percentage ?? scheme.achievement_percentage ?? 0)}
                  <span className="text-sm font-semibold">{scheme.percentage ?? scheme.achievement_percentage ?? 0}%</span>
                </div>
              </div>
              {(scheme.target !== undefined || scheme.achievement !== undefined) && (
                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                  {scheme.target !== undefined && <span>Target: {scheme.target.toLocaleString()}</span>}
                  {scheme.target !== undefined && scheme.achievement !== undefined && <span>•</span>}
                  {scheme.achievement !== undefined && <span>Achieved: {scheme.achievement.toLocaleString()}</span>}
                </div>
              )}
              {scheme.current_status && (
                <div className="text-xs text-muted-foreground mt-1">
                  Status: {scheme.current_status}
                </div>
              )}
              {/* Progress Bar */}
              <div className="mt-2 w-full bg-muted rounded-full h-1.5">
                <div 
                  className={`h-1.5 rounded-full transition-all ${
                    (scheme.percentage || scheme.achievement_percentage || 0) >= 90 ? 'bg-green-600' :
                    (scheme.percentage || scheme.achievement_percentage || 0) >= 70 ? 'bg-yellow-600' :
                    'bg-red-600'
                  }`}
                  style={{ width: `${Math.min(scheme.percentage || scheme.achievement_percentage || 0, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SectorCard;
