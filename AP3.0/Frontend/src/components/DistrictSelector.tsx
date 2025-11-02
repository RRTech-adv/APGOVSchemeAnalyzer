import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MapPin } from "lucide-react";

interface DistrictSelectorProps {
  selectedDistrict: string;
  onDistrictChange: (district: string) => void;
  districts: string[];
}

const DistrictSelector = ({ selectedDistrict, onDistrictChange, districts }: DistrictSelectorProps) => {
  return (
    <div className="bg-card rounded-lg shadow-card p-6 border border-border">
      <div className="flex items-center space-x-2 mb-4">
        <MapPin className="h-5 w-5 text-primary" />
        <h2 className="text-xl font-semibold text-foreground">Select District</h2>
      </div>
      <Select value={selectedDistrict} onValueChange={onDistrictChange}>
        <SelectTrigger className="w-full h-12 text-base">
          <SelectValue placeholder="Choose a district..." />
        </SelectTrigger>
        <SelectContent className="bg-popover z-50">
          {districts.map((district) => (
            <SelectItem key={district} value={district} className="text-base py-3">
              {district}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default DistrictSelector;
