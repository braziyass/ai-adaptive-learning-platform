import { NavLink, Outlet } from "react-router-dom";
import { BookOpen, ClipboardCheck, LayoutDashboard, LogOut, Shield, Sparkles, Users, UserRound } from "lucide-react";
import type { ComponentType } from "react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getCurrentRole, getDashboardPath, type Role } from "@/lib/auth";
import { useLogoutMutation } from "@/lib/query-hooks";
import { cn } from "@/lib/utils";

const roleLabels: Record<Role, string> = {
  administrator: "Administrateur",
  teacher: "Enseignant",
  student: "Étudiant",
};

const roleNav: Record<Role, Array<{ to: string; label: string; icon: ComponentType<{ className?: string }> }>> = {
  administrator: [
    { to: "/admin/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
    { to: "/admin/students", label: "Étudiants", icon: Users },
    { to: "/admin/teachers", label: "Enseignants", icon: UserRound },
    { to: "/statistics", label: "Statistiques", icon: Sparkles },
  ],
  teacher: [
    { to: "/teacher/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
    { to: "/teacher/students", label: "Étudiants", icon: Users },
    { to: "/lessons", label: "Leçons", icon: BookOpen },
    { to: "/quiz", label: "Quiz", icon: ClipboardCheck },
    { to: "/validation-test", label: "Test de validation", icon: Shield },
    { to: "/statistics", label: "Statistiques", icon: Sparkles },
  ],
  student: [
    { to: "/student/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
    { to: "/lessons", label: "Leçons", icon: BookOpen },
    { to: "/quiz", label: "Quiz", icon: ClipboardCheck },
    { to: "/placement-test", label: "Test de positionnement", icon: Shield },
    { to: "/validation-test", label: "Test de validation", icon: Sparkles },
    { to: "/statistics", label: "Statistiques", icon: Sparkles },
  ],
};

export function AppShell() {
  const role = getCurrentRole() ?? "student";
  const logout = useLogoutMutation();

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.16),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(15,23,42,0.10),_transparent_32%),linear-gradient(180deg,_#f8fafc_0%,_#eff6ff_100%)] text-slate-950">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col lg:flex-row">
        <aside className="border-b border-slate-200/80 bg-white/80 px-4 py-4 backdrop-blur lg:min-h-screen lg:w-80 lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between gap-3 lg:flex-col lg:items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Apprentissage adaptatif</p>
              <h2 className="mt-2 font-display text-2xl font-semibold">Plateforme d'apprentissage IA</h2>
            </div>
            <Badge variant="secondary" className="capitalize">{roleLabels[role]}</Badge>
          </div>

          <Separator className="my-4" />

          <nav className="flex gap-2 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible">
            {roleNav[role].map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "flex min-w-max items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                    isActive ? "bg-slate-950 text-white shadow-soft" : "bg-white text-slate-700 hover:bg-slate-100",
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Session</p>
            <p className="mt-2 text-sm text-slate-700">Vous êtes connecté à {getDashboardPath(role)}</p>
            <Button variant="outline" className="mt-4 w-full justify-start" onClick={() => logout.mutate()}>
              <LogOut className="mr-2 h-4 w-4" />
              Se déconnecter
            </Button>
          </div>
        </aside>

        <main className="flex-1 px-4 py-4 sm:px-6 lg:px-8 lg:py-8">
          <div className="rounded-[2rem] border border-white/60 bg-white/75 p-4 shadow-soft backdrop-blur xl:p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
