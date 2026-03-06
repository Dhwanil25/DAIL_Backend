import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/topbar";
import { CommandPalette } from "@/components/layout/command-palette";
import { Providers } from "@/components/providers";
import { MobileNavProvider } from "@/components/layout/mobile-nav-context";


const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LIA - Legal Intelligence Dashboard",
  description: "Modern analytics and management for AI litigation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-navy-deep text-foreground antialiased`}>
        <Providers>
          <MobileNavProvider>
            <div className="flex h-screen w-full overflow-hidden">
              <Sidebar />
              <div className="flex flex-1 flex-col overflow-hidden">
                <TopBar />
                <main className="flex-1 overflow-y-auto scroll-smooth bg-navy-deep relative">
                  {/* Background Glows */}
                  <div className="absolute top-0 right-0 -z-10 h-[500px] w-[500px] bg-teal-accent/5 blur-[120px]" />
                  <div className="absolute bottom-0 left-0 -z-10 h-[500px] w-[500px] bg-violet-accent/5 blur-[120px]" />

                  <div className="p-4 md:p-8">
                    {children}
                  </div>
                </main>
              </div>
            </div>
            <CommandPalette />
          </MobileNavProvider>
        </Providers>
      </body>

    </html>
  );
}
