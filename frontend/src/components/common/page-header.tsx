import { Badge } from "@/components/ui/badge";

export function PageHeader({ title, description, eyebrow }: { title: string; description: string; eyebrow?: string }) {
  return (
    <div className="space-y-3">
      {eyebrow ? <Badge variant="secondary" className="w-fit uppercase tracking-[0.2em]">{eyebrow}</Badge> : null}
      <div className="space-y-2">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">{title}</h1>
        <p className="max-w-3xl text-sm leading-7 text-slate-600 md:text-base">{description}</p>
      </div>
    </div>
  );
}
