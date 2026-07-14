import { Hero } from "@/widgets/Hero";
import { Services } from "@/widgets/Services";
import { About, Contacts, Footer, Portfolio, Reviews } from "@/widgets/Sections";
import { isMiniApp } from "@/shared/lib/telegram";

export function HomePage() {
  const miniApp = isMiniApp();
  return (
    <main>
      <Hero />
      <Services />
      <Portfolio />
      <About />
      <Reviews />
      {/* В Mini App футер/контакты-визитку скрываем (SPEC §6.1). */}
      {!miniApp && <Contacts />}
      {!miniApp && <Footer />}
    </main>
  );
}
