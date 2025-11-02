import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, List } from "lucide-react";

interface SectorData {
  [sectorName: string]: {
    name: string;
    sub_category?: string;
    current_status?: string;
    achievement_percentage?: number;
    percentage?: number;
    data_source?: string;
    remarks?: string;
    additional_details?: Record<string, any>;
    is_info_only?: boolean;
  }[];
}

interface SectorDataViewProps {
  data: SectorData;
}

const SectorDataView = ({ data }: SectorDataViewProps) => {
  const [viewMode, setViewMode] = useState<"accordion" | "table">("accordion");

  // Transform data into a flat list for table view
  const allEntries: Array<{
    sector: string;
    subcategory: string;
    status: string;
    percentage: number | string;
    dataSource: string;
    remarks: string;
    additionalDetails: Record<string, any>;
  }> = [];

  Object.entries(data || {}).forEach(([sectorName, schemes]) => {
    if (Array.isArray(schemes)) {
      schemes.forEach((scheme) => {
        // Ensure additional_details is properly extracted - check multiple possible paths
        let additionalDetails: Record<string, any> = {};
        
        // Try different property names and nested paths
        if (scheme.additional_details && typeof scheme.additional_details === 'object') {
          additionalDetails = scheme.additional_details;
        } else if (scheme.additionalDetails && typeof scheme.additionalDetails === 'object') {
          additionalDetails = scheme.additionalDetails;
        } else if (scheme.information?.additional_details) {
          additionalDetails = scheme.information.additional_details;
        } else if (scheme.info?.additional_details) {
          additionalDetails = scheme.info.additional_details;
        }
        
        // Debug logging to see what we have
        if (Object.keys(additionalDetails).length > 0) {
          console.log(`Found additional details for ${sectorName}/${scheme.sub_category || scheme.name}:`, additionalDetails);
        } else {
          console.log(`No additional details found for ${sectorName}/${scheme.sub_category || scheme.name}. Scheme object:`, scheme);
        }
        
        allEntries.push({
          sector: sectorName,
          subcategory: scheme.sub_category || scheme.name,
          status: scheme.current_status || "N/A",
          percentage: scheme.percentage ?? scheme.achievement_percentage ?? "N/A",
          dataSource: scheme.data_source || scheme.dataSource || "N/A",
          remarks: scheme.remarks || "N/A",
          additionalDetails: additionalDetails,
        });
      });
    }
  });
  
  // Debug: log all entries to see what we have
  console.log('All table entries with additional details:', allEntries.map(e => ({
    sector: e.sector,
    subcategory: e.subcategory,
    hasDetails: Object.keys(e.additionalDetails).length > 0,
    detailsCount: Object.keys(e.additionalDetails).length
  })));

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes("complete") || statusLower.includes("done")) {
      return "bg-green-100 text-green-800 border-green-200";
    }
    if (statusLower.includes("progress") || statusLower.includes("track")) {
      return "bg-blue-100 text-blue-800 border-blue-200";
    }
    if (statusLower.includes("pending") || statusLower.includes("delayed")) {
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    }
    return "bg-gray-100 text-gray-800 border-gray-200";
  };

  const getPercentageColor = (percentage: number | string) => {
    if (typeof percentage === "string") return "";
    if (percentage >= 90) return "text-green-600 font-semibold";
    if (percentage >= 70) return "text-yellow-600 font-semibold";
    return "text-red-600 font-semibold";
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>District Data Overview</CardTitle>
          <div className="flex gap-2">
            <Button
              variant={viewMode === "accordion" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("accordion")}
              className="gap-2"
            >
              <FileText className="h-4 w-4" />
              Accordion
            </Button>
            <Button
              variant={viewMode === "table" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("table")}
              className="gap-2"
            >
              <List className="h-4 w-4" />
              Table
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {viewMode === "accordion" ? (
          <Accordion type="multiple" className="w-full">
            {Object.entries(data || {}).map(([sectorName, schemes]) => {
              if (!Array.isArray(schemes)) return null;
              return (
              <AccordionItem key={sectorName} value={sectorName}>
                <AccordionTrigger className="text-lg font-semibold">
                  <div className="flex items-center justify-between w-full pr-4">
                    <span>{sectorName}</span>
                    <Badge variant="outline" className="ml-2">
                      {schemes.length} {schemes.length === 1 ? "item" : "items"}
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2">
                    {schemes.map((scheme, index) => (
                      <Card key={index} className="bg-muted/50">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base">{scheme.name}</CardTitle>
                          {scheme.sub_category && scheme.sub_category !== scheme.name && (
                            <p className="text-sm text-muted-foreground">
                              Sub-Category: {scheme.sub_category}
                            </p>
                          )}
                        </CardHeader>
                        <CardContent className="space-y-2">
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {scheme.current_status && (
                              <div>
                                <span className="font-medium">Status: </span>
                                <Badge
                                  variant="outline"
                                  className={getStatusColor(scheme.current_status)}
                                >
                                  {scheme.current_status}
                                </Badge>
                              </div>
                            )}
                            {(scheme.percentage !== undefined ||
                              scheme.achievement_percentage !== undefined) &&
                              !scheme.is_info_only && (
                                <div>
                                  <span className="font-medium">Achievement: </span>
                                  <span
                                    className={getPercentageColor(
                                      scheme.percentage ?? scheme.achievement_percentage ?? 0
                                    )}
                                  >
                                    {scheme.percentage ?? scheme.achievement_percentage ?? 0}%
                                  </span>
                                </div>
                              )}
                            {scheme.data_source && (
                              <div>
                                <span className="font-medium">Data Source: </span>
                                <span className="text-muted-foreground">{scheme.data_source}</span>
                              </div>
                            )}
                          </div>
                          {scheme.remarks && (
                            <div className="text-sm">
                              <span className="font-medium">Remarks: </span>
                              <span className="text-muted-foreground">{scheme.remarks}</span>
                            </div>
                          )}
                          {scheme.additional_details &&
                            Object.keys(scheme.additional_details).length > 0 && (
                              <div className="mt-3 pt-3 border-t">
                                <div className="text-sm font-semibold mb-2">
                                  Additional Information:
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                  {Object.entries(scheme.additional_details).map(
                                    ([key, value]) => (
                                      <div key={key} className="text-sm">
                                        <span className="font-medium">
                                          {key.replace(/_/g, " ").replace(/\b\w/g, (l) =>
                                            l.toUpperCase()
                                          )}
                                          :{" "}
                                        </span>
                                        <span className="text-muted-foreground">
                                          {String(value)}
                                        </span>
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
              );
            })}
          </Accordion>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Sector</TableHead>
                  <TableHead>Sub-Category</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Percentage</TableHead>
                  <TableHead>Data Source</TableHead>
                  <TableHead>Remarks</TableHead>
                  <TableHead>Additional Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allEntries.length > 0 ? (
                  allEntries.map((entry, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{entry.sector}</TableCell>
                      <TableCell>{entry.subcategory}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getStatusColor(entry.status)}>
                          {entry.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {typeof entry.percentage === "number" ? (
                          <span className={getPercentageColor(entry.percentage)}>
                            {entry.percentage}%
                          </span>
                        ) : (
                          <span className="text-muted-foreground">{entry.percentage}</span>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">{entry.dataSource}</TableCell>
                      <TableCell className="max-w-xs truncate">{entry.remarks}</TableCell>
                       <TableCell className="max-w-2xl">
                         {entry.additionalDetails && 
                          typeof entry.additionalDetails === 'object' && 
                          !Array.isArray(entry.additionalDetails) &&
                          Object.keys(entry.additionalDetails).length > 0 ? (
                           <div className="bg-muted/20 p-2 rounded border">
                             <div className="space-y-1.5 max-h-60 overflow-y-auto">
                               {Object.entries(entry.additionalDetails).map(([key, value]) => {
                                 // Ensure value is not null or undefined
                                 const displayValue = value !== null && value !== undefined ? String(value) : 'N/A';
                                 return (
                                   <div key={key} className="text-xs py-1 flex items-start gap-2">
                                     <span className="text-primary font-bold mt-0.5 flex-shrink-0">•</span>
                                     <div className="flex-1 min-w-0">
                                       <span className="font-semibold text-foreground break-words">
                                         {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}:
                                       </span>
                                       <span className="text-muted-foreground break-words ml-1">
                                         {displayValue}
                                       </span>
                                     </div>
                                   </div>
                                 );
                               })}
                             </div>
                           </div>
                         ) : (
                           <span className="text-muted-foreground text-xs italic">No additional details</span>
                         )}
                       </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      No data available
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SectorDataView;

