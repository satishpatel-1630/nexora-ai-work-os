import type { Metadata } from "next";
export const metadata: Metadata = { title: "NEXORA", description: "Personal AI Work OS" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body style={{margin:0}}>{children}</body></html>;
}
