import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search } from "lucide-react";
import { Applicant } from "@/lib/mockData";

interface ApplicantsTableProps {
  applicants: Applicant[];
}

export function ApplicantsTable({ applicants }: ApplicantsTableProps) {
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState<string>("all");

  const filteredApplicants = applicants.filter((applicant) => {
    const matchesSearch = applicant.name.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = riskFilter === "all" || applicant.riskLevel === riskFilter;
    return matchesSearch && matchesRisk;
  });

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case "Bajo":
        return "default";
      case "Medio":
        return "secondary";
      case "Alto":
        return "destructive";
      default:
        return "default";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nombre..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={riskFilter} onValueChange={setRiskFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filtrar por riesgo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los riesgos</SelectItem>
            <SelectItem value="Bajo">Riesgo Bajo</SelectItem>
            <SelectItem value="Medio">Riesgo Medio</SelectItem>
            <SelectItem value="Alto">Riesgo Alto</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Edad</TableHead>
              <TableHead>Ingresos</TableHead>
              <TableHead>Monto</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Prob. Mora</TableHead>
              <TableHead>Riesgo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredApplicants.map((applicant) => (
              <TableRow key={applicant.id}>
                <TableCell className="font-medium">{applicant.name}</TableCell>
                <TableCell>{applicant.age}</TableCell>
                <TableCell>${applicant.income.toLocaleString()}</TableCell>
                <TableCell>${applicant.creditAmount.toLocaleString()}</TableCell>
                <TableCell>{applicant.employmentStatus}</TableCell>
                <TableCell>{(applicant.defaultProbability * 100).toFixed(1)}%</TableCell>
                <TableCell>
                  <Badge variant={getRiskBadgeVariant(applicant.riskLevel)}>
                    {applicant.riskLevel}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
