import './globals.css';
import Navbar from '@/components/Navbar';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'VaartaVerse — Classical IR Folk Tale Lineage Engine',
  description: 'A Classical Information Retrieval (IR) System exploring Indian folk tale variants across Panchatantra, Jataka, Hitopadesha, Vikramaditya, and regional traditions.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500 font-mono">
          VaartaVerse Classical IR Engine • Hand-Crafted Inverted Index, VSM TF-IDF, Rocchio Feedback & MAP/nDCG Evaluation
        </footer>
      </body>
    </html>
  );
}
