import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { X, Send, Bot, User } from "lucide-react";

// Component to format chat messages with proper rendering
const FormattedMessage = ({ content }: { content: string }) => {
  // Split content into lines for processing
  const lines = content.split('\n');
  const formattedLines: React.ReactNode[] = [];
  let inBulletList = false;
  let inNumberedList = false;
  let bulletItems: string[] = [];
  let numberedItems: string[] = [];

  const flushBulletList = () => {
    if (bulletItems.length > 0) {
      formattedLines.push(
        <ul key={`bullet-list-${formattedLines.length}`} className="list-disc list-inside space-y-1 ml-2 mt-2 mb-2">
          {bulletItems.map((item, idx) => (
            <li key={idx} className="text-sm leading-relaxed">{item.trim()}</li>
          ))}
        </ul>
      );
      bulletItems = [];
      inBulletList = false;
    }
  };

  const flushNumberedList = () => {
    if (numberedItems.length > 0) {
      formattedLines.push(
        <ol key={`numbered-list-${formattedLines.length}`} className="list-decimal list-inside space-y-1 ml-2 mt-2 mb-2">
          {numberedItems.map((item, idx) => (
            <li key={idx} className="text-sm leading-relaxed">{item.trim()}</li>
          ))}
        </ol>
      );
      numberedItems = [];
      inNumberedList = false;
    }
  };

  const flushAllLists = () => {
    flushBulletList();
    flushNumberedList();
  };

  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    
    // Check for numbered list first (more specific)
    if (/^\d+\.\s/.test(trimmedLine)) {
      flushBulletList(); // Flush bullet list if we switch to numbered
      if (!inNumberedList) {
        inNumberedList = true;
      }
      const itemText = trimmedLine.replace(/^\d+\.\s/, '');
      numberedItems.push(itemText);
      return;
    }

    // Check for bullet points (-, •, *)
    if (/^[-•*]\s/.test(trimmedLine)) {
      flushNumberedList(); // Flush numbered list if we switch to bullet
      if (!inBulletList) {
        inBulletList = true;
      }
      const itemText = trimmedLine.replace(/^[-•*]\s/, '');
      bulletItems.push(itemText);
      return;
    }

    // Flush all lists if we hit a non-list item
    if (inBulletList || inNumberedList) {
      flushAllLists();
    }

    // Handle empty lines
    if (trimmedLine === '') {
      formattedLines.push(<br key={`br-${index}`} />);
      return;
    }

    // Handle bold text (markdown style)
    const processBold = (text: string): React.ReactNode[] => {
      const parts: React.ReactNode[] = [];
      const boldRegex = /\*\*(.+?)\*\*/g;
      let lastIndex = 0;
      let match;
      
      while ((match = boldRegex.exec(text)) !== null) {
        if (match.index > lastIndex) {
          parts.push(text.substring(lastIndex, match.index));
        }
        parts.push(<strong key={`bold-${parts.length}`} className="font-semibold">{match[1]}</strong>);
        lastIndex = match.index + match[0].length;
      }
      
      if (lastIndex < text.length) {
        parts.push(text.substring(lastIndex));
      }
      
      return parts.length > 0 ? parts : [text];
    };

    // Check for headers (## or ###)
    if (trimmedLine.startsWith('###')) {
      formattedLines.push(
        <h3 key={`h3-${index}`} className="font-semibold text-base mt-3 mb-2">
          {processBold(trimmedLine.replace(/^###\s*/, ''))}
        </h3>
      );
    } else if (trimmedLine.startsWith('##')) {
      formattedLines.push(
        <h2 key={`h2-${index}`} className="font-bold text-lg mt-4 mb-2">
          {processBold(trimmedLine.replace(/^##\s*/, ''))}
        </h2>
      );
    } else {
      // Regular paragraph
      formattedLines.push(
        <p key={`p-${index}`} className="text-sm leading-relaxed mb-2 last:mb-0">
          {processBold(trimmedLine)}
        </p>
      );
    }
  });

  // Flush any remaining list items
  flushAllLists();

  return <div className="space-y-1">{formattedLines}</div>;
};

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  district: string;
}

const ChatInterface = ({ isOpen, onClose, district }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hello! I'm your AI assistant for ${district} district analytics. Ask me anything about schemes, achievements, or specific sectors.`
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    const queryText = input;
    setInput("");
    setIsLoading(true);

    try {
      // Call backend API
      const { api } = await import("@/lib/api");
      const response = await api.chat(queryText, district);
      
      const assistantMessage: Message = {
        role: "assistant",
        content: response.response
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] z-50 animate-slide-in">
      <Card className="h-full flex flex-col shadow-elevated">
        <CardHeader className="gradient-government text-primary-foreground">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Bot className="h-5 w-5" />
              <span>AI Assistant</span>
            </CardTitle>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={onClose}
              className="text-primary-foreground hover:bg-white/20"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-sm text-primary-foreground/90 mt-1">
            {district} District Analytics
          </p>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
          <div 
            className="flex-1 overflow-y-auto p-4"
            ref={scrollRef}
            style={{ 
              maxHeight: 'calc(600px - 180px)',
              scrollBehavior: 'smooth'
            }}
          >
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-2 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.role === "assistant" && (
                    <div className="bg-primary text-primary-foreground rounded-full p-2 flex-shrink-0">
                      <Bot className="h-4 w-4" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <FormattedMessage content={message.content} />
                    ) : (
                      <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                    )}
                  </div>
                  {message.role === "user" && (
                    <div className="bg-accent text-accent-foreground rounded-full p-2 flex-shrink-0">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex items-start space-x-2">
                  <div className="bg-primary text-primary-foreground rounded-full p-2 flex-shrink-0">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="bg-muted text-foreground rounded-lg p-3">
                    <p className="text-sm">Analyzing data...</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="p-4 border-t border-border">
            <div className="flex space-x-2">
              <Input
                placeholder="Ask about schemes, achievements..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                disabled={isLoading}
              />
              <Button 
                onClick={handleSend} 
                disabled={isLoading || !input.trim()}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <style>{`
        @keyframes slide-in {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
