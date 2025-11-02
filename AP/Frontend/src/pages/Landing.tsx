import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import apLogo from "@/assets/ap-logo.png";
import apHero from "@/assets/ap-hero.jpg";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url(${apHero})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary/90 via-primary/80 to-accent/70" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          {/* Logo */}
          <div className="flex justify-center mb-8 animate-fade-in">
            <div className="bg-white/95 p-6 rounded-full shadow-elevated">
              <img 
                src={apLogo} 
                alt="Arunachal Pradesh Government Logo" 
                className="h-32 w-32"
              />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 animate-fade-in-up">
            Arunachal Pradesh
          </h1>
          <h2 className="text-3xl md:text-4xl font-semibold text-white/95 mb-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            Development Monitoring System
          </h2>
          
          {/* Tagline */}
          <p className="text-xl md:text-2xl text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            Comprehensive District Development Dashboard
            <br />
            <span className="text-lg text-white/80">Government of Arunachal Pradesh</span>
          </p>

          {/* CTA Button */}
          <div className="animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <Button 
              size="xl" 
              variant="hero"
              onClick={() => navigate('/login')}
              className="bg-white text-primary hover:bg-white/90 shadow-2xl"
            >
              Login to Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Stats Bar */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-4xl font-bold text-white mb-2">25+</div>
              <div className="text-white/90">Districts</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-4xl font-bold text-white mb-2">8</div>
              <div className="text-white/90">Key Sectors</div>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <div className="text-4xl font-bold text-white mb-2">Real-time</div>
              <div className="text-white/90">Analytics</div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Animations */}
      <style>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 1s ease-out;
        }

        .animate-fade-in-up {
          animation: fade-in-up 1s ease-out;
          animation-fill-mode: both;
        }
      `}</style>
    </div>
  );
};

export default Landing;
