import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";
import DistrictSelector from "@/components/DistrictSelector";
import DocumentUpload from "@/components/DocumentUpload";
import SectorCard from "@/components/SectorCard";
import ChartsSection from "@/components/ChartsSection";
import ChatInterface from "@/components/ChatInterface";
import { GraduationCap, Heart, Sprout, Home, Lightbulb, Factory, Wifi, Users, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const sectorIcons: any = {
  "Health": <Heart className="h-5 w-5 text-primary" />,
  "Education": <GraduationCap className="h-5 w-5 text-primary" />,
  "Agriculture": <Sprout className="h-5 w-5 text-primary" />,
  "Infrastructure": <Factory className="h-5 w-5 text-primary" />,
  "Social Welfare": <Users className="h-5 w-5 text-primary" />,
  "Technology": <Wifi className="h-5 w-5 text-primary" />,
  "Housing": <Home className="h-5 w-5 text-primary" />,
  "Energy": <Lightbulb className="h-5 w-5 text-primary" />
};

const Dashboard = () => {
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [districts, setDistricts] = useState<string[]>([]);
  const [districtData, setDistrictData] = useState<any>(null);
  const [analytics, setAnalytics] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const { toast } = useToast();

  // Fetch districts on mount
  useEffect(() => {
    const fetchDistricts = async () => {
      try {
        setIsLoading(true);
        const districtList = await api.getDistricts();
        setDistricts(districtList || []);
        if (districtList && districtList.length > 0 && !selectedDistrict) {
          setSelectedDistrict(districtList[0]);
        } else if (!districtList || districtList.length === 0) {
          // Even if no districts, allow the UI to render
          console.log("No districts found in database");
        }
      } catch (error) {
        console.error("Error fetching districts:", error);
        setDistricts([]);
        toast({
          title: "Connection Error",
          description: "Unable to connect to backend API. Please ensure the backend is running on http://localhost:8000",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchDistricts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch district data when district changes
  useEffect(() => {
    if (!selectedDistrict) return;

    const fetchDistrictData = async () => {
      setIsLoadingData(true);
      try {
        const [data, analyticsData] = await Promise.all([
          api.getDistrictData(selectedDistrict),
          api.getDistrictAnalytics(selectedDistrict).catch(() => ({}))
        ]);
        
        // Transform data to match the expected format
        const transformedData = {
          district: data.district || selectedDistrict,
          sectors: {} as any
        };

        // Transform sectors data
        Object.entries(data.sectors || {}).forEach(([sectorName, subCategories]: [string, any]) => {
          const schemes: any[] = [];
          Object.entries(subCategories || {}).forEach(([subCatName, subCatData]: [string, any]) => {
            const actionPoints = subCatData?.action_points || [];
            actionPoints.forEach((ap: any) => {
              // Calculate target and achievement from percentage if needed
              // If we have percentage, estimate target=100 and achievement=percentage
              const percentage = ap.achievement_percentage || 0;
              const estimatedTarget = 100; // Default target
              const estimatedAchievement = Math.round(estimatedTarget * (percentage / 100));
              
              schemes.push({
                name: ap.action_name || subCatName,
                current_status: ap.current_status,
                achievement_percentage: percentage,
                data_source: ap.data_source,
                remarks: ap.remarks,
                // Fields required by SectorCard
                percentage: percentage,
                target: estimatedTarget,
                achievement: estimatedAchievement
              });
            });
          });
          if (schemes.length > 0) {
            transformedData.sectors[sectorName] = schemes;
          }
        });

        setDistrictData(transformedData);
        setAnalytics(analyticsData);
      } catch (error) {
        toast({
          title: "Error",
          description: `Failed to load data for ${selectedDistrict}. ${error instanceof Error ? error.message : ''}`,
          variant: "destructive"
        });
        console.error("Error fetching district data:", error);
        setDistrictData({ district: selectedDistrict, sectors: {} });
      } finally {
        setIsLoadingData(false);
      }
    };

    fetchDistrictData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDistrict]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading districts...</p>
        </div>
      </div>
    );
  }

  // Show empty state but still render the UI so users can upload
  if (districts.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar onChatClick={() => setIsChatOpen(true)} />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12 mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Welcome to Development Dashboard
            </h2>
            <p className="text-lg text-muted-foreground mb-4">
              No districts found in the database
            </p>
            <p className="text-sm text-muted-foreground mb-8">
              Upload a document to get started and create your first district entry.
            </p>
          </div>
          
          {/* Show upload component even without districts */}
          <div className="max-w-2xl mx-auto">
            <DocumentUpload district={selectedDistrict || "New District"} />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar onChatClick={() => setIsChatOpen(true)} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* District Selector and Upload Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            {districts.length > 0 && selectedDistrict ? (
              <DistrictSelector
                selectedDistrict={selectedDistrict}
                onDistrictChange={setSelectedDistrict}
                districts={districts}
              />
            ) : (
              <div className="bg-card rounded-lg shadow-card p-6 border border-border">
                <p className="text-muted-foreground">Loading districts...</p>
              </div>
            )}
          </div>
          <div>
            <DocumentUpload district={selectedDistrict || districts[0] || "New District"} />
          </div>
        </div>

        {/* Analytics Summary Header */}
        {selectedDistrict && (
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-2">
              {selectedDistrict} District Analytics
            </h2>
            <p className="text-muted-foreground">
              Comprehensive development monitoring across all sectors
            </p>
          </div>
        )}

        {isLoadingData ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary mr-3" />
            <p className="text-muted-foreground">Loading district data...</p>
          </div>
        ) : (
          <>
            {/* Charts Section */}
            {districtData && Object.keys(districtData.sectors || {}).length > 0 && (
              <div className="mb-8">
                <ChartsSection data={districtData} />
              </div>
            )}

            {/* Sector Cards */}
            {districtData && Object.keys(districtData.sectors || {}).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(districtData.sectors || {}).map(([sector, schemes]: [string, any]) => (
                  <SectorCard
                    key={sector}
                    title={sector}
                    schemes={schemes}
                    icon={sectorIcons[sector] || <Sprout className="h-5 w-5 text-primary" />}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-lg text-muted-foreground mb-2">No data available for {selectedDistrict}</p>
                <p className="text-sm text-muted-foreground">Upload documents to see analytics and sector information.</p>
              </div>
            )}
          </>
        )}
      </main>

      {/* Floating Chat Button - Always visible */}
      {!isChatOpen && (
        <Button
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-elevated gradient-accent"
          size="icon"
          onClick={() => setIsChatOpen(true)}
        >
          <span className="text-2xl">💬</span>
        </Button>
      )}

      {/* Chat Interface - Only show if district is selected */}
      {selectedDistrict && (
        <ChatInterface
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
          district={selectedDistrict}
        />
      )}
    </div>
  );
};

export default Dashboard;
