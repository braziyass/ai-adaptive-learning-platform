import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { useStudentCurrentLevelQuery, useStudentProfileQuery } from "@/lib/query-hooks";

export function PlacementTestPage() {
  const profileQuery = useStudentProfileQuery();
  const levelQuery = useStudentCurrentLevelQuery();

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Test de positionnement" title="Résumé du positionnement" description="Le backend expose actuellement le niveau attribué et le score de positionnement plutôt qu'un test interactif, donc cette page se concentre sur le résultat généré." />

      <Card>
        <CardHeader>
          <CardTitle>Aperçu du positionnement</CardTitle>
          <CardDescription>Dérivé des points de terminaison du profil étudiant et du niveau actuel.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <Info label="Étudiant" value={`${profileQuery.data?.first_name ?? ""} ${profileQuery.data?.last_name ?? ""}`.trim()} />
          <Info label="Score de positionnement" value={String(profileQuery.data?.placement_score ?? 0)} />
          <Info label="Niveau actuel" value={String(levelQuery.data?.current_level ?? profileQuery.data?.current_level ?? 0)} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Orientation</CardTitle>
          <CardDescription>Utilisez le score de positionnement pour déterminer votre parcours d'apprentissage recommandé.</CardDescription>
        </CardHeader>
        <CardContent>
          <Badge variant="secondary">Connecté au backend</Badge>
        </CardContent>
      </Card>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-2 font-medium text-slate-950">{value || "—"}</p>
    </div>
  );
}
