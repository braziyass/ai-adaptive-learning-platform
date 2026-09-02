import { useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, LockKeyhole, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createSessionFromTokens, getAuthSession, getDashboardPath } from "@/lib/auth";
import { useLoginMutation } from "@/lib/query-hooks";

export function LoginPage() {
  const session = getAuthSession();
  const navigate = useNavigate();
  const location = useLocation();
  const login = useLoginMutation();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("adminpass123");

  useEffect(() => {
    if (session) {
      navigate(getDashboardPath(session.role), { replace: true });
    }
  }, [navigate, session]);

  if (session) {
    return <Navigate to={getDashboardPath(session.role)} replace />;
  }

  return (
    <div className="grid min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(2,132,199,0.22),_transparent_28%),linear-gradient(180deg,_#f8fafc_0%,_#e2e8f0_100%)] lg:grid-cols-[1.1fr_0.9fr]">
      <div className="flex flex-col justify-between px-6 py-8 text-slate-950 sm:px-10 lg:px-16 lg:py-12">
        <div>
          <Badge className="bg-slate-950 text-white">Plateforme d'apprentissage adaptatif IA</Badge>
          <h1 className="mt-8 max-w-2xl font-display text-5xl font-semibold tracking-tight md:text-7xl">
            Un apprentissage personnalisé, orchestré par l'IA et guidé par le progrès.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
            Connectez-vous pour consulter les parcours d'apprentissage, gérer les étudiants et les enseignants, et suivre les résultats de positionnement et de validation sur toute la plateforme.
          </p>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          {[
            ["Contenu appuyé par la RAG", "Les leçons et les tests restent liés aux extraits du programme récupérés."],
            ["Tableaux de bord par rôle", "Les expériences administrateur, enseignant et étudiant partagent une seule interface."],
            ["Analyses en temps réel", "Les indicateurs de progression, de positionnement et de validation se mettent à jour depuis l'API."],
          ].map(([title, description]) => (
            <div key={title} className="rounded-2xl border border-slate-200 bg-white/75 p-5 shadow-soft backdrop-blur">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-white">
                <Sparkles className="h-5 w-5" />
              </div>
              <h2 className="mt-4 font-display text-lg font-semibold">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-center px-6 py-10 sm:px-10 lg:px-16">
        <Card className="w-full max-w-lg border-white/70 bg-white/85">
          <CardHeader>
            <CardDescription>Bon retour</CardDescription>
            <CardTitle className="text-3xl">Connectez-vous pour continuer</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              className="space-y-5"
              onSubmit={(event) => {
                event.preventDefault();
                login.mutate(
                  { email, password },
                  {
                    onSuccess: (tokens) => {
                      const session = createSessionFromTokens(tokens.access_token, tokens.refresh_token);
                      navigate(getDashboardPath(session.role), { replace: true });
                    },
                  },
                );
              }}
            >
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input id="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="vous@exemple.com" autoComplete="email" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <Input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" autoComplete="current-password" />
              </div>
              {login.isError ? <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">Connexion impossible. Vérifiez vos identifiants et la connexion au backend.</p> : null}
              <Button type="submit" size="lg" className="w-full" disabled={login.isPending}>
                <LockKeyhole className="mr-2 h-4 w-4" />
                {login.isPending ? "Connexion en cours..." : "Se connecter"}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
