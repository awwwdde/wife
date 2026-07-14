import { motion } from "framer-motion";
import { Link } from "react-router-dom";

// Hero: заголовок + CTA. Появление — Framer Motion; параллакс/pin (GSAP) — фаза 2.
export function Hero() {
  return (
    <section className="min-h-[90vh] flex flex-col justify-center px-6 md:px-16">
      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="font-script text-terracotta text-2xl mb-4"
      >
        Ангелина 
      </motion.p>
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.1 }}
        className="font-serif text-5xl md:text-7xl leading-tight max-w-3xl"
      >
        ASKBROWS
        <span className="block italic text-terracotta">бровки и реснички</span>
      </motion.h1>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mt-10"
      >
        <Link
          to="/booking"
          className="inline-block bg-graphite text-cream px-8 py-4 rounded-full text-lg hover:bg-terracotta transition-colors"
        >
          Записаться
        </Link>
      </motion.div>
    </section>
  );
}
