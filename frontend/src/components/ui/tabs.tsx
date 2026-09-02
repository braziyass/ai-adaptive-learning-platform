import * as React from "react";

import { cn } from "@/lib/utils";

const TabsContext = React.createContext<{ value: string; setValue: (value: string) => void } | null>(null);

export function Tabs({ value, onValueChange, children, className }: React.PropsWithChildren<{ value: string; onValueChange: (value: string) => void; className?: string }>) {
  return <TabsContext.Provider value={{ value, setValue: onValueChange }}><div className={className}>{children}</div></TabsContext.Provider>;
}

export function TabsList({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("inline-flex rounded-2xl bg-slate-100 p-1 text-slate-600", className)} {...props} />;
}

export function TabsTrigger({ value, className, children }: React.PropsWithChildren<{ value: string; className?: string }>) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsTrigger must be used within Tabs");
  const active = context.value === value;
  return (
    <button type="button" onClick={() => context.setValue(value)} className={cn("rounded-xl px-4 py-2 text-sm font-medium transition", active ? "bg-white text-slate-950 shadow-sm" : "hover:text-slate-950", className)}>
      {children}
    </button>
  );
}

export function TabsContent({ value, className, children }: React.PropsWithChildren<{ value: string; className?: string }>) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsContent must be used within Tabs");
  if (context.value !== value) return null;
  return <div className={className}>{children}</div>;
}
