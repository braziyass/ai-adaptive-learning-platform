import { useEffect, useMemo, useState, type FormEvent } from "react";
import { FileUp, Loader2, PencilLine, Plus, Sparkles, Trash2, Wand2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import {
  useAdminCourseLessonsQuery,
  useAdminCoursesQuery,
  useAdminPlacementTestQuery,
  useAdminStudentsQuery,
  useAdminTeachersQuery,
  useCreateStudentMutation,
  useCreateTeacherMutation,
  useDeleteStudentMutation,
  useDeleteTeacherMutation,
  useGenerateArtifactMutation,
  useUpdatePlacementTestMutation,
  useUpdateStudentMutation,
  useUpdateTeacherMutation,
  useUploadPdfMutation,
} from "@/lib/query-hooks";
import type { AdminPlacementTestQuestionInput, GeneratedArtifactResponse, PdfIngestionResponse, StudentFormValues } from "@/types/api";

const emptyStudent: StudentFormValues = {
  first_name: "",
  last_name: "",
  email: "",
  password: "Password123!",
  current_level: 1,
  placement_score: 0,
};

const emptyTeacher = {
  first_name: "",
  last_name: "",
  email: "",
  password: "Password123!",
};

export function AdminDashboardPage() {
  const studentsQuery = useAdminStudentsQuery();
  const teachersQuery = useAdminTeachersQuery();
  const uploadPdf = useUploadPdfMutation();
  const generateArtifact = useGenerateArtifactMutation();
  const createStudent = useCreateStudentMutation();
  const updateStudent = useUpdateStudentMutation();
  const deleteStudent = useDeleteStudentMutation();
  const createTeacher = useCreateTeacherMutation();
  const updateTeacher = useUpdateTeacherMutation();
  const deleteTeacher = useDeleteTeacherMutation();
  const placementTestQuery = useAdminPlacementTestQuery();
  const updatePlacementTest = useUpdatePlacementTestMutation();

  const [studentForm, setStudentForm] = useState<StudentFormValues>(emptyStudent);
  const [teacherForm, setTeacherForm] = useState(emptyTeacher);
  const [editingStudentId, setEditingStudentId] = useState<number | null>(null);
  const [editingTeacherId, setEditingTeacherId] = useState<number | null>(null);
  const [selectedPdf, setSelectedPdf] = useState<File | null>(null);
  const [pdfIngestion, setPdfIngestion] = useState<PdfIngestionResponse | null>(null);
  const [pdfIngestionError, setPdfIngestionError] = useState<string | null>(null);
  const [artifactType, setArtifactType] = useState<GeneratedArtifactResponse["artifact_type"]>("lesson");
  const [generationTitle, setGenerationTitle] = useState("Nouvelle leçon");
  const [generationSubject, setGenerationSubject] = useState("Mathématiques");
  const [generationLevel, setGenerationLevel] = useState("1");
  const [generationCourseId, setGenerationCourseId] = useState<number | null>(null);
  const [generationCourseTitle, setGenerationCourseTitle] = useState("");
  const [generationLessonId, setGenerationLessonId] = useState<number | null>(null);
  const [generationQuestionCount, setGenerationQuestionCount] = useState("5");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [generationStudentId, setGenerationStudentId] = useState("");
  const [generationInstruction, setGenerationInstruction] = useState("");
  const [generationContext, setGenerationContext] = useState("{}");
  const [generatedArtifact, setGeneratedArtifact] = useState<GeneratedArtifactResponse | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);

  const coursesQuery = useAdminCoursesQuery();
  const courseLessonsQuery = useAdminCourseLessonsQuery(generationCourseId);
  const needsCourse = artifactType === "lesson" || artifactType === "quiz";
  const needsLesson = artifactType === "quiz";
  const needsQuestionCount = artifactType === "quiz";

  const [placementGenTitle, setPlacementGenTitle] = useState("Test de positionnement");
  const [placementGenSubject, setPlacementGenSubject] = useState("Général");
  const [placementGenCount, setPlacementGenCount] = useState("40");
  const [placementGenError, setPlacementGenError] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editSubject, setEditSubject] = useState("");
  const [editQuestions, setEditQuestions] = useState<AdminPlacementTestQuestionInput[]>([]);
  const [loadedPlacementTestId, setLoadedPlacementTestId] = useState<number | null>(null);
  const [placementSaveError, setPlacementSaveError] = useState<string | null>(null);
  const [placementSaveSuccess, setPlacementSaveSuccess] = useState(false);

  useEffect(() => {
    if (placementTestQuery.data && placementTestQuery.data.placement_test_id !== loadedPlacementTestId) {
      setEditTitle(placementTestQuery.data.title);
      setEditSubject(placementTestQuery.data.subject);
      setEditQuestions(
        placementTestQuery.data.questions.map((q) => ({
          question: q.question,
          question_type: q.question_type,
          options: q.options,
          answer: q.answer,
          explanation: q.explanation,
        })),
      );
      setLoadedPlacementTestId(placementTestQuery.data.placement_test_id);
    }
  }, [placementTestQuery.data, loadedPlacementTestId]);

  function updatePlacementQuestion(index: number, patch: Partial<AdminPlacementTestQuestionInput>) {
    setEditQuestions((current) => current.map((question, i) => (i === index ? { ...question, ...patch } : question)));
  }

  function removePlacementQuestion(index: number) {
    setEditQuestions((current) => current.filter((_, i) => i !== index));
  }

  function addPlacementQuestion() {
    setEditQuestions((current) => [...current, { question: "", question_type: "multiple_choice", options: [], answer: "", explanation: "" }]);
  }

  async function handleGeneratePlacementTest(event: FormEvent) {
    event.preventDefault();
    setPlacementGenError(null);
    try {
      await generateArtifact.mutateAsync({
        artifactType: "placement_test",
        payload: {
          title: placementGenTitle,
          subject: placementGenSubject,
          level: 1,
          question_count: Number(placementGenCount) || 40,
          locale: "fr",
        },
      });
      setLoadedPlacementTestId(null);
      await placementTestQuery.refetch();
    } catch (error) {
      setPlacementGenError(error instanceof Error ? error.message : "Impossible de générer le test de positionnement.");
    }
  }

  async function handleSavePlacementTest() {
    setPlacementSaveError(null);
    setPlacementSaveSuccess(false);
    try {
      await updatePlacementTest.mutateAsync({ title: editTitle, subject: editSubject, questions: editQuestions });
      setPlacementSaveSuccess(true);
    } catch (error) {
      setPlacementSaveError(error instanceof Error ? error.message : "Impossible d'enregistrer les modifications.");
    }
  }

  const studentCount = studentsQuery.data?.length ?? 0;
  const teacherCount = teachersQuery.data?.length ?? 0;
  const recentStudents = useMemo(() => studentsQuery.data?.slice(0, 5) ?? [], [studentsQuery.data]);
  const recentTeachers = useMemo(() => teachersQuery.data?.slice(0, 5) ?? [], [teachersQuery.data]);

  function parseOptionalNumber(value: string) {
    if (!value.trim()) {
      return null;
    }

    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function renderGeneratedArtifactPreview() {
    if (!generatedArtifact) {
      return null;
    }

    const payload = generatedArtifact.payload as Record<string, unknown>;
    const title = String(payload.title ?? generatedArtifact.title);
    const content = typeof payload.content === "string" ? payload.content : null;
    const summary = typeof payload.summary === "string" ? payload.summary : null;
    const objectives = Array.isArray(payload.objectives) ? payload.objectives.filter((item) => typeof item === "string") as string[] : [];
    const references = Array.isArray(payload.references) ? payload.references.filter((item) => typeof item === "string") as string[] : [];
    const questions = Array.isArray(payload.questions) ? payload.questions.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object") : [];

    if (generatedArtifact.artifact_type === "lesson") {
      return (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="capitalize">leçon</Badge>
            <span className="font-medium text-slate-950">{title}</span>
          </div>
          {summary ? <p className="rounded-2xl border border-slate-200 bg-white p-4 text-sm leading-7 text-slate-700"><strong>Résumé :</strong> {summary}</p> : null}
          {objectives.length ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
              <p className="font-medium text-slate-950">Objectifs d'apprentissage</p>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {objectives.map((objective) => <li key={objective}>{objective}</li>)}
              </ul>
            </div>
          ) : null}
          {content ? <p className="whitespace-pre-wrap rounded-2xl border border-slate-200 bg-white p-4 text-sm leading-7 text-slate-700">{content}</p> : null}
          {references.length ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
              <p className="font-medium text-slate-950">Références</p>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {references.map((reference) => <li key={reference}>{reference}</li>)}
              </ul>
            </div>
          ) : null}
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary" className="capitalize">{generatedArtifact.artifact_type.replace(/_/g, " ")}</Badge>
          <span className="font-medium text-slate-950">{title}</span>
          {generatedArtifact.artifact_id ? <span className="text-slate-500">ID {generatedArtifact.artifact_id}</span> : null}
        </div>
        {questions.length ? (
          <div className="space-y-3">
            {questions.map((question, index) => {
              const questionText = String(question.question ?? `Question ${index + 1}`);
              const options = Array.isArray(question.options) ? question.options.filter((item) => typeof item === "string") as string[] : [];
              const explanation = typeof question.explanation === "string" ? question.explanation : null;

              return (
                <div key={`${title}-${index}`} className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="font-medium text-slate-950">{index + 1}. {questionText}</p>
                  {options.length ? (
                    <ul className="mt-3 space-y-2">
                      {options.map((option) => <li key={option} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">{option}</li>)}
                    </ul>
                  ) : null}
                  {explanation ? <p className="mt-3 text-sm leading-6 text-slate-600"><strong>Explication :</strong> {explanation}</p> : null}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">Aucune question n'a été renvoyée dans la charge utile.</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Administrateur"
        title="Centre de contrôle des personnes et des accès"
        description="Créez, modifiez et auditez les étudiants et les enseignants tout en surveillant les effectifs de la plateforme."
      />

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard title="Étudiants" value={String(studentCount)} description="Profils étudiants gérés et chargés depuis le backend." />
        <StatCard title="Enseignants" value={String(teacherCount)} description="Comptes enseignants disponibles pour le suivi pédagogique." />
        <StatCard title="Formulaires étudiants" value={editingStudentId ? "Modifier" : "Créer"} description="L'éditeur étudiant prend en charge le CRUD complet via le backend." />
        <StatCard title="Formulaires enseignants" value={editingTeacherId ? "Modifier" : "Créer"} description="Les fiches enseignants peuvent être créées et mises à jour sur place." />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Étudiants</CardTitle>
            <CardDescription>Gérez les comptes étudiants et les métadonnées de positionnement. Un mot de passe est requis lors de la création d'un compte.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form
              className="grid gap-4 md:grid-cols-2"
              onSubmit={(event) => {
                event.preventDefault();
                if (editingStudentId) {
                  updateStudent.mutate(
                    { studentId: editingStudentId, payload: studentForm },
                    { onSuccess: () => { setEditingStudentId(null); setStudentForm(emptyStudent); } },
                  );
                } else {
                  createStudent.mutate(studentForm, { onSuccess: () => setStudentForm(emptyStudent) });
                }
              }}
            >
              <div className="space-y-2"><Label>Prénom</Label><Input value={studentForm.first_name} onChange={(event) => setStudentForm((current) => ({ ...current, first_name: event.target.value }))} /></div>
              <div className="space-y-2"><Label>Nom</Label><Input value={studentForm.last_name} onChange={(event) => setStudentForm((current) => ({ ...current, last_name: event.target.value }))} /></div>
              <div className="space-y-2 md:col-span-2"><Label>E-mail</Label><Input type="email" value={studentForm.email} onChange={(event) => setStudentForm((current) => ({ ...current, email: event.target.value }))} /></div>
              <div className="space-y-2"><Label>Mot de passe</Label><Input type="password" value={studentForm.password} onChange={(event) => setStudentForm((current) => ({ ...current, password: event.target.value }))} /></div>
              <p className="md:col-span-2 text-xs text-slate-500">Utilisez au moins 8 caractères. Les nouveaux comptes étudiants utilisent un mot de passe temporaire tant que vous ne le remplacez pas.</p>
              {editingStudentId ? (
                <>
                  <div className="space-y-2"><Label>Niveau actuel</Label><Input type="number" min={1} value={studentForm.current_level} onChange={(event) => setStudentForm((current) => ({ ...current, current_level: Number(event.target.value) }))} /></div>
                  <div className="space-y-2"><Label>Score de positionnement</Label><Input type="number" min={0} value={studentForm.placement_score} onChange={(event) => setStudentForm((current) => ({ ...current, placement_score: Number(event.target.value) }))} /></div>
                </>
              ) : (
                <p className="md:col-span-2 text-xs text-slate-500">Le niveau et le score de positionnement sont attribués automatiquement après le test de positionnement de l'étudiant.</p>
              )}
              <div className="md:col-span-2 flex flex-wrap gap-3">
                <Button type="submit"><Plus className="mr-2 h-4 w-4" />{editingStudentId ? "Mettre à jour l'étudiant" : "Créer l'étudiant"}</Button>
                {editingStudentId ? <Button type="button" variant="outline" onClick={() => { setEditingStudentId(null); setStudentForm(emptyStudent); }}>Annuler</Button> : null}
              </div>
            </form>

            <div className="overflow-x-auto rounded-2xl border border-slate-200">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead>Niveau</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {studentsQuery.data?.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>{student.first_name} {student.last_name}</TableCell>
                      <TableCell>{student.email}</TableCell>
                      <TableCell>{student.current_level}</TableCell>
                      <TableCell>{student.placement_score}</TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => { setEditingStudentId(student.id); setStudentForm({ ...studentForm, first_name: student.first_name, last_name: student.last_name, email: student.email, current_level: student.current_level, placement_score: student.placement_score, password: studentForm.password || "password123" }); }}><PencilLine className="h-4 w-4" /></Button>
                          <Button variant="destructive" size="sm" onClick={() => deleteStudent.mutate(student.id)}><Trash2 className="h-4 w-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Enseignants</CardTitle>
            <CardDescription>Gérez les comptes enseignants et leurs accès. Un mot de passe est requis lors de la création d'un compte.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form
              className="grid gap-4 md:grid-cols-2"
              onSubmit={(event) => {
                event.preventDefault();
                if (editingTeacherId) {
                  updateTeacher.mutate(
                    { teacherId: editingTeacherId, payload: teacherForm },
                    { onSuccess: () => { setEditingTeacherId(null); setTeacherForm(emptyTeacher); } },
                  );
                } else {
                  createTeacher.mutate(teacherForm, { onSuccess: () => setTeacherForm(emptyTeacher) });
                }
              }}
            >
              <div className="space-y-2"><Label>Prénom</Label><Input value={teacherForm.first_name} onChange={(event) => setTeacherForm((current) => ({ ...current, first_name: event.target.value }))} /></div>
              <div className="space-y-2"><Label>Nom</Label><Input value={teacherForm.last_name} onChange={(event) => setTeacherForm((current) => ({ ...current, last_name: event.target.value }))} /></div>
              <div className="space-y-2 md:col-span-2"><Label>E-mail</Label><Input type="email" value={teacherForm.email} onChange={(event) => setTeacherForm((current) => ({ ...current, email: event.target.value }))} /></div>
              <div className="space-y-2 md:col-span-2"><Label>Mot de passe</Label><Input type="password" value={teacherForm.password} onChange={(event) => setTeacherForm((current) => ({ ...current, password: event.target.value }))} /></div>
              <p className="md:col-span-2 text-xs text-slate-500">Utilisez au moins 8 caractères. Les nouveaux comptes enseignants utilisent un mot de passe temporaire tant que vous ne le remplacez pas.</p>
              <div className="md:col-span-2 flex flex-wrap gap-3">
                <Button type="submit"><Plus className="mr-2 h-4 w-4" />{editingTeacherId ? "Mettre à jour l'enseignant" : "Créer l'enseignant"}</Button>
                {editingTeacherId ? <Button type="button" variant="outline" onClick={() => { setEditingTeacherId(null); setTeacherForm(emptyTeacher); }}>Annuler</Button> : null}
              </div>
            </form>

            <div className="overflow-x-auto rounded-2xl border border-slate-200">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {teachersQuery.data?.map((teacher) => (
                    <TableRow key={teacher.id}>
                      <TableCell>{teacher.first_name} {teacher.last_name}</TableCell>
                      <TableCell>{teacher.email}</TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => { setEditingTeacherId(teacher.id); setTeacherForm({ ...teacherForm, first_name: teacher.first_name, last_name: teacher.last_name, email: teacher.email, password: teacherForm.password || "password123" }); }}><PencilLine className="h-4 w-4" /></Button>
                          <Button variant="destructive" size="sm" onClick={() => deleteTeacher.mutate(teacher.id)}><Trash2 className="h-4 w-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Étudiants récents</CardTitle><CardDescription>Les cinq premiers enregistrements renvoyés par le backend.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {recentStudents.map((student) => <div key={student.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">{student.first_name} {student.last_name} · Niveau {student.current_level} · Score {student.placement_score}</div>)}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Enseignants récents</CardTitle><CardDescription>Les cinq premiers enregistrements renvoyés par le backend.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {recentTeachers.map((teacher) => <div key={teacher.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">{teacher.first_name} {teacher.last_name} · {teacher.email}</div>)}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Importer une source PDF</CardTitle>
            <CardDescription>Envoyez un PDF au pipeline d'ingestion du backend avant de générer des ressources pédagogiques.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <form
              className="space-y-4"
              onSubmit={async (event) => {
                event.preventDefault();
                setPdfIngestionError(null);

                if (!selectedPdf) {
                  setPdfIngestionError("Sélectionnez un PDF avant de l'envoyer.");
                  return;
                }

                try {
                  const result = await uploadPdf.mutateAsync(selectedPdf);
                  setPdfIngestion(result);
                } catch (error) {
                  const message = error instanceof Error ? error.message : "Impossible d'envoyer le PDF.";
                  setPdfIngestionError(message);
                }
              }}
            >
              <div className="space-y-2">
                <Label htmlFor="ai-pdf-file">Fichier PDF</Label>
                <Input
                  id="ai-pdf-file"
                  type="file"
                  accept="application/pdf"
                  onChange={(event) => {
                    setSelectedPdf(event.target.files?.[0] ?? null);
                    setPdfIngestionError(null);
                    setPdfIngestion(null);
                  }}
                />
              </div>

              <div className="flex flex-wrap gap-3">
                <Button type="submit" disabled={uploadPdf.isPending}>
                  {uploadPdf.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileUp className="mr-2 h-4 w-4" />}
                  {uploadPdf.isPending ? "Envoi en cours..." : "Envoyer et ingérer"}
                </Button>
              </div>
            </form>

            {pdfIngestionError ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{pdfIngestionError}</div> : null}

            {pdfIngestion ? (
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
                <p className="font-medium">{pdfIngestion.source_document}</p>
                <p className="mt-1">{pdfIngestion.chunk_count} fragments indexés pour la recherche.</p>
                <p className="mt-1 break-all text-xs text-emerald-800">IDs vectoriels : {pdfIngestion.vector_ids.join(", ")}</p>
              </div>
            ) : null}

            <p className="text-sm leading-6 text-slate-600">
              Le point de terminaison d'envoi enregistre le PDF dans le dossier de stockage du backend et l'indexe immédiatement pour le worker de génération.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Générer une ressource</CardTitle>
            <CardDescription>Créez une leçon, un quiz, un test de positionnement ou un test de validation à partir du contexte PDF indexé.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <form
              className="space-y-4"
              onSubmit={async (event) => {
                event.preventDefault();
                setGenerationError(null);

                let parsedContext: Record<string, unknown> = {};
                if (generationContext.trim()) {
                  try {
                    const value = JSON.parse(generationContext) as unknown;
                    if (!value || typeof value !== "object" || Array.isArray(value)) {
                      throw new Error("Le contexte supplémentaire doit être un objet JSON.");
                    }
                    parsedContext = value as Record<string, unknown>;
                  } catch (error) {
                    setGenerationError(error instanceof Error ? error.message : "JSON invalide dans le contexte supplémentaire.");
                    return;
                  }
                }

                if (needsCourse && generationCourseId === null && !generationCourseTitle.trim()) {
                  setGenerationError("Sélectionnez un cours ou indiquez le nom d'un nouveau cours.");
                  return;
                }
                if (needsLesson && generationLessonId === null) {
                  setGenerationError("Sélectionnez une leçon existante pour générer un quiz.");
                  return;
                }

                try {
                  const result = await generateArtifact.mutateAsync({
                    artifactType,
                    payload: {
                      title: generationTitle,
                      subject: generationSubject,
                      level: Number(generationLevel),
                      course_id: generationCourseId,
                      course_title: needsCourse && generationCourseId === null ? generationCourseTitle.trim() : undefined,
                      lesson_id: needsLesson ? generationLessonId : null,
                      question_count: needsQuestionCount ? Number(generationQuestionCount) || 5 : undefined,
                      student_id: showAdvanced ? parseOptionalNumber(generationStudentId) : null,
                      instruction: generationInstruction.trim() || undefined,
                      extra_context: Object.keys(parsedContext).length > 0 ? parsedContext : undefined,
                      locale: "fr",
                    },
                  });
                  setGeneratedArtifact(result);
                } catch (error) {
                  const message = error instanceof Error ? error.message : "Impossible de générer la ressource.";
                  setGenerationError(message);
                }
              }}
            >
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="artifact-type">Type de ressource</Label>
                  <select
                    id="artifact-type"
                    value={artifactType}
                    onChange={(event) => {
                      setArtifactType(event.target.value as GeneratedArtifactResponse["artifact_type"]);
                      setGenerationCourseId(null);
                      setGenerationCourseTitle("");
                      setGenerationLessonId(null);
                    }}
                    className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                  >
                    <option value="lesson">Leçon</option>
                    <option value="quiz">Quiz</option>
                    <option value="validation_test">Test de validation</option>
                  </select>
                  <p className="text-xs text-slate-500">Le test de positionnement se gère séparément, dans la section « Test de positionnement » ci-dessous.</p>
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="generation-title">Titre</Label>
                  <Input id="generation-title" value={generationTitle} onChange={(event) => setGenerationTitle(event.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="generation-subject">Matière</Label>
                  <Input id="generation-subject" value={generationSubject} onChange={(event) => setGenerationSubject(event.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="generation-level">Niveau</Label>
                  <Input id="generation-level" type="number" min={1} value={generationLevel} onChange={(event) => setGenerationLevel(event.target.value)} />
                </div>
                {needsCourse ? (
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="generation-course">Cours</Label>
                    <select
                      id="generation-course"
                      value={generationCourseId ?? ""}
                      onChange={(event) => {
                        const value = event.target.value ? Number(event.target.value) : null;
                        setGenerationCourseId(value);
                        setGenerationLessonId(null);
                      }}
                      className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                    >
                      <option value="">{needsLesson ? "Sélectionner un cours..." : "+ Nouveau cours"}</option>
                      {coursesQuery.data?.map((course) => (
                        <option key={course.id} value={course.id}>{course.title} · {course.subject}</option>
                      ))}
                    </select>
                    {!needsLesson && generationCourseId === null ? (
                      <Input
                        placeholder="Nom du nouveau cours (ex. Mathématiques CE1)"
                        value={generationCourseTitle}
                        onChange={(event) => setGenerationCourseTitle(event.target.value)}
                      />
                    ) : null}
                  </div>
                ) : null}
                {needsLesson ? (
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="generation-lesson">Leçon</Label>
                    <select
                      id="generation-lesson"
                      value={generationLessonId ?? ""}
                      disabled={generationCourseId === null}
                      onChange={(event) => setGenerationLessonId(event.target.value ? Number(event.target.value) : null)}
                      className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200 disabled:opacity-50"
                    >
                      <option value="">Sélectionner une leçon...</option>
                      {courseLessonsQuery.data?.map((lesson) => (
                        <option key={lesson.id} value={lesson.id}>{lesson.title} (niveau {lesson.level})</option>
                      ))}
                    </select>
                    {generationCourseId !== null && courseLessonsQuery.data?.length === 0 ? (
                      <p className="text-xs text-amber-600">Ce cours n'a pas encore de leçon. Générez-en une d'abord.</p>
                    ) : null}
                  </div>
                ) : null}
                {needsQuestionCount ? (
                  <div className="space-y-2">
                    <Label htmlFor="generation-question-count">Nombre de questions</Label>
                    <Input
                      id="generation-question-count"
                      type="number"
                      min={1}
                      max={50}
                      value={generationQuestionCount}
                      onChange={(event) => setGenerationQuestionCount(event.target.value)}
                    />
                  </div>
                ) : null}
                <div className="space-y-2 md:col-span-2">
                  <button
                    type="button"
                    className="text-xs font-medium text-slate-500 underline"
                    onClick={() => setShowAdvanced((current) => !current)}
                  >
                    {showAdvanced ? "Masquer les options avancées" : "Afficher les options avancées"}
                  </button>
                  {showAdvanced ? (
                    <div className="mt-2 space-y-2">
                      <Label htmlFor="generation-student-id">ID de l'étudiant (régénération personnalisée)</Label>
                      <Input id="generation-student-id" type="number" min={1} value={generationStudentId} onChange={(event) => setGenerationStudentId(event.target.value)} />
                    </div>
                  ) : null}
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="generation-instruction">Consigne</Label>
                  <Textarea id="generation-instruction" value={generationInstruction} onChange={(event) => setGenerationInstruction(event.target.value)} placeholder="Ajoutez des contraintes supplémentaires ou l'objectif d'apprentissage visé." />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="generation-context">Contexte supplémentaire JSON</Label>
                  <Textarea id="generation-context" value={generationContext} onChange={(event) => setGenerationContext(event.target.value)} placeholder='{"focus": "past tense review"}' />
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Button type="submit" disabled={generateArtifact.isPending}>
                  {generateArtifact.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                  {generateArtifact.isPending ? "Génération en cours..." : "Générer la ressource"}
                </Button>
              </div>
            </form>

            {generationError ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{generationError}</div> : null}

            {generatedArtifact ? (
              <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
                {renderGeneratedArtifactPreview()}
              </div>
            ) : null}

            <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
              <div className="flex items-center gap-2 text-slate-900">
                <Wand2 className="h-4 w-4" />
                Conseils de génération
              </div>
              <p className="mt-2 leading-6">
Pour une leçon, choisissez un cours existant ou créez-en un nouveau (le niveau détermine automatiquement où elle est rangée dans le cours). Pour un quiz, choisissez le cours puis la leçon à laquelle il doit être rattaché, et le nombre de questions souhaité.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test de positionnement</CardTitle>
          <CardDescription>
            Un test unique, commun à tous les étudiants de votre établissement, généré à partir du contenu de tous vos cours.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <form className="grid gap-4 md:grid-cols-3" onSubmit={handleGeneratePlacementTest}>
            <div className="space-y-2">
              <Label htmlFor="placement-gen-title">Titre</Label>
              <Input id="placement-gen-title" value={placementGenTitle} onChange={(event) => setPlacementGenTitle(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="placement-gen-subject">Libellé</Label>
              <Input id="placement-gen-subject" value={placementGenSubject} onChange={(event) => setPlacementGenSubject(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="placement-gen-count">Nombre de questions</Label>
              <Input id="placement-gen-count" type="number" min={1} max={100} value={placementGenCount} onChange={(event) => setPlacementGenCount(event.target.value)} />
            </div>
            <div className="md:col-span-3">
              <Button type="submit" disabled={generateArtifact.isPending}>
                {generateArtifact.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                {placementTestQuery.data ? "Regénérer le test (remplace l'actuel)" : "Générer le test"}
              </Button>
              <p className="mt-2 text-xs text-slate-500">
                Regénérer remplace entièrement le test actif : tous les étudiants qui n'ont pas encore passé le test de positionnement verront le nouveau.
              </p>
            </div>
          </form>

          {placementGenError ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{placementGenError}</div> : null}

          {placementTestQuery.isLoading ? <p className="text-sm text-slate-500">Chargement du test actif...</p> : null}
          {!placementTestQuery.isLoading && !placementTestQuery.data ? (
            <p className="text-sm text-slate-500">Aucun test de positionnement n'a encore été généré pour votre établissement.</p>
          ) : null}

          {placementTestQuery.data ? (
            <div className="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">Test actif</Badge>
                  <span className="text-sm text-slate-600">{editQuestions.length} question(s)</span>
                </div>
                <Button type="button" onClick={handleSavePlacementTest} disabled={updatePlacementTest.isPending}>
                  {updatePlacementTest.isPending ? "Enregistrement..." : "Enregistrer les modifications"}
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="placement-edit-title">Titre du test</Label>
                  <Input id="placement-edit-title" value={editTitle} onChange={(event) => setEditTitle(event.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="placement-edit-subject">Libellé</Label>
                  <Input id="placement-edit-subject" value={editSubject} onChange={(event) => setEditSubject(event.target.value)} />
                </div>
              </div>

              {placementSaveError ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{placementSaveError}</div> : null}
              {placementSaveSuccess ? <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">Modifications enregistrées.</div> : null}

              <div className="max-h-[32rem] space-y-3 overflow-y-auto pr-1">
                {editQuestions.map((question, index) => (
                  <div key={index} className="space-y-2 rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Question {index + 1}</span>
                      <Button type="button" variant="destructive" size="sm" onClick={() => removePlacementQuestion(index)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    <Textarea
                      value={question.question}
                      onChange={(event) => updatePlacementQuestion(index, { question: event.target.value })}
                      placeholder="Énoncé de la question"
                    />
                    <div className="grid gap-2 md:grid-cols-2">
                      <select
                        value={question.question_type}
                        onChange={(event) => updatePlacementQuestion(index, { question_type: event.target.value })}
                        className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                      >
                        <option value="multiple_choice">Choix multiple</option>
                        <option value="true_false">Vrai / Faux</option>
                        <option value="short_answer">Réponse courte</option>
                      </select>
                      <Input
                        value={question.answer ?? ""}
                        onChange={(event) => updatePlacementQuestion(index, { answer: event.target.value })}
                        placeholder="Réponse correcte"
                      />
                    </div>
                    {question.question_type === "multiple_choice" ? (
                      <Input
                        value={question.options.join(", ")}
                        onChange={(event) => updatePlacementQuestion(index, { options: event.target.value.split(",").map((option) => option.trim()).filter(Boolean) })}
                        placeholder="Options séparées par des virgules"
                      />
                    ) : null}
                    <Textarea
                      value={question.explanation ?? ""}
                      onChange={(event) => updatePlacementQuestion(index, { explanation: event.target.value })}
                      placeholder="Explication (optionnel)"
                    />
                  </div>
                ))}
              </div>

              <Button type="button" variant="outline" onClick={addPlacementQuestion}>
                <Plus className="mr-2 h-4 w-4" />
                Ajouter une question
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
