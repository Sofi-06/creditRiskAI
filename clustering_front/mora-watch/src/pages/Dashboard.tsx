import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ThemeToggle } from "@/components/ThemeToggle";
import { StatCard } from "@/components/StatCard";
import { ApplicantsTable } from "@/components/ApplicantsTable";
import { RiskDistributionChart } from "@/components/RiskDistributionChart";
import { IncomeCorrelationChart } from "@/components/IncomeCorrelationChart";
import { EmploymentChart } from "@/components/EmploymentChart";
import { Button } from "@/components/ui/button";
import { Building2, Users, TrendingUp, DollarSign, AlertTriangle, LogOut } from "lucide-react";
import { mockApplicants, getStatistics } from "@/lib/mockData";
import { toast } from "sonner";

const Dashboard = () => {
  const navigate = useNavigate();
  const stats = getStatistics();

  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    if (!isAuthenticated) {
      navigate("/");
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    toast.success("Sesión cerrada exitosamente");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">CreditRisk Analytics</h1>
              <p className="text-xs text-muted-foreground">Panel de análisis crediticio</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Solicitantes"
            value={stats.totalApplicants}
            icon={Users}
            description="Aplicaciones totales"
          />
          <StatCard
            title="% Riesgo Alto"
            value={`${stats.highRiskPercentage}%`}
            icon={AlertTriangle}
            description="Solicitantes de alto riesgo"
          />
          <StatCard
            title="Ingreso Promedio"
            value={`$${stats.averageIncome.toLocaleString()}`}
            icon={DollarSign}
            description="Ingreso medio de solicitantes"
          />
          <StatCard
            title="Mora Promedio"
            value={`${(parseFloat(stats.averageDefault) * 100).toFixed(1)}%`}
            icon={TrendingUp}
            description="Probabilidad media de impago"
          />
        </div>

        {/* Charts */}
        <div className="grid gap-6 lg:grid-cols-2">
          <RiskDistributionChart applicants={mockApplicants} />
          <IncomeCorrelationChart applicants={mockApplicants} />
        </div>

        <div className="grid gap-6">
          <EmploymentChart applicants={mockApplicants} />
        </div>

        {/* Applicants Table */}
        <div className="space-y-4">
          <div>
            <h2 className="text-2xl font-bold">Solicitantes</h2>
            <p className="text-muted-foreground">Lista completa de aplicaciones con análisis de riesgo</p>
          </div>
          <ApplicantsTable applicants={mockApplicants} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
