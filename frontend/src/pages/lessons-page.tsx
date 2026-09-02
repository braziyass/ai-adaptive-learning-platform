import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { useStudentUnlockedLessonsQuery } from "@/lib/query-hooks";

export function LessonsPage() {
  const lessonsQuery = useStudentUnlockedLessonsQuery();

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Leçons" title="Contenu de leçon débloqué" description="Consultez le contenu renvoyé par le backend et reprenez exactement l'extrait du programme qui vous est disponible." />

      <div className="grid gap-4 md:grid-cols-2">
        {lessonsQuery.data?.map((lesson) => (
          <Card key={lesson.lesson_id}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle>{lesson.lesson_title}</CardTitle>
                  <CardDescription>{lesson.chapter_title} · Ordre du chapitre {lesson.chapter_order}</CardDescription>
                </div>
                <Badge variant={lesson.completed ? "success" : "warning"}>{lesson.completed ? "Terminée" : "Débloquée"}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{lesson.content}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
