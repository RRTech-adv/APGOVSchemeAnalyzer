import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DocumentUploadProps {
  district: string;
}

const DocumentUpload = ({ district }: DocumentUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const fileType = selectedFile.name.split('.').pop()?.toLowerCase();
      
      if (fileType && ['pdf', 'doc', 'docx', 'txt'].includes(fileType)) {
        setFile(selectedFile);
        setUploadStatus("idle");
      } else {
        toast({
          title: "Invalid File Type",
          description: "Please upload PDF, DOC, DOCX, or TXT files only.",
          variant: "destructive"
        });
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");

    try {
      // Call backend API
      const { api } = await import("@/lib/api");
      const response = await api.uploadDocument(file, district);
      
      if (response.status === "success" || response.status === "partial_success") {
        setUploadStatus("success");
        toast({
          title: "Upload Successful",
          description: response.message || `Document uploaded for ${district} district. Data extraction initiated.`,
        });
        
        // Reset after success
        setTimeout(() => {
          setFile(null);
          setUploadStatus("idle");
          // Reload page to refresh data
          window.location.reload();
        }, 3000);
      } else {
        throw new Error(response.message || "Upload failed");
      }
      
    } catch (error) {
      setUploadStatus("error");
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "There was an error uploading the document. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Upload className="h-5 w-5 text-primary" />
          <span>Upload District Document</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Upload PDF, DOC, or TXT files containing scheme data for <span className="font-semibold text-foreground">{district}</span> district.
        </div>

        <div className="space-y-2">
          <Label htmlFor="file-upload" className="text-sm font-medium">
            Select Document
          </Label>
          <div className="flex items-center space-x-2">
            <Input
              id="file-upload"
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              disabled={isUploading}
              className="flex-1"
            />
          </div>
        </div>

        {file && (
          <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
            <FileText className="h-5 w-5 text-primary" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            {uploadStatus === "success" && (
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
            )}
            {uploadStatus === "error" && (
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
            )}
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="w-full"
          size="lg"
        >
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload & Extract Data
            </>
          )}
        </Button>

        <div className="text-xs text-muted-foreground space-y-1">
          <p>• Supported formats: PDF, DOC, DOCX, TXT</p>
          <p>• Maximum file size: 20MB</p>
          <p>• Data will be automatically extracted and processed</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentUpload;
