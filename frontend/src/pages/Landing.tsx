import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <Card className="w-[90%] max-w-2xl p-8 space-y-8">
        <div className="space-y-4 text-center">
          <h1 className="text-4xl font-bold tracking-tight">
            Welcome to ThreadHive
          </h1>
          <p className="text-muted-foreground text-lg">
            Join our community to share your thoughts and connect with others
          </p>
        </div>

        <div className="flex flex-col space-y-4">
          <Button
            size="lg"
            className="w-full"
            onClick={() => navigate("/login")}
          >
            Login
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>

          <Button
            size="lg"
            variant="outline"
            className="w-full"
            onClick={() => navigate("/register")}
          >
            Create an account
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </Card>
    </div>
  );
}
