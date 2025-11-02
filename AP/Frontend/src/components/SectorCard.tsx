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
  additional_details?: Record<string, any>;
  sub_category?: string;
  is_info_only?: boolean;
}

interface SectorCardProps {
  title: string;
  schemes: Scheme[];
  icon: React.ReactNode;
}

const SectorCard = ({ title, schemes, icon }: SectorCardProps) => {
  // Calculate average percentage only from schemes with percentages
  const schemesWithPercentage = schemes.filter(s => (s.percentage !== undefined || s.achievement_percentage !== undefined) && !s.is_info_only);
  const avgPercentage = schemesWithPercentage.length > 0 
    ? schemesWithPercentage.reduce((sum, s) => sum + (s.percentage || s.achievement_percentage || 0), 0) / schemesWithPercentage.length 
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
                {(scheme.percentage !== undefined || scheme.achievement_percentage !== undefined) && !scheme.is_info_only && (
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(scheme.percentage ?? scheme.achievement_percentage ?? 0)}
                    <span className="text-sm font-semibold">{scheme.percentage ?? scheme.achievement_percentage ?? 0}%</span>
                  </div>
                )}
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
              {scheme.data_source && (
                <div className="text-xs text-muted-foreground mt-1">
                  Data Source: {scheme.data_source}
                </div>
              )}
              {scheme.remarks && (
                <div className="text-xs text-muted-foreground mt-1">
                  Remarks: {scheme.remarks}
                </div>
              )}
              {/* Display all additional details */}
              {scheme.additional_details && Object.keys(scheme.additional_details).length > 0 && (
                <div className="mt-2 space-y-1">
                  <div className="text-xs font-semibold text-foreground">Additional Information:</div>
                  {Object.entries(scheme.additional_details).map(([key, value]) => (
                    <div key={key} className="text-xs text-muted-foreground ml-2">
                      <span className="font-medium">{key.replace(/_/g, ' ')}:</span> {String(value)}
                    </div>
                  ))}
                </div>
              )}
              {/* Progress Bar - only show if percentage is available */}
              {(scheme.percentage !== undefined || scheme.achievement_percentage !== undefined) && (
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
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SectorCard;
