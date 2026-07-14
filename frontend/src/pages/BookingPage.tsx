import { Link } from "react-router-dom";
import { BookingWizard } from "@/features/booking/BookingWizard";

export function BookingPage() {
  return (
    <main>
      <p>
        <Link to="/">← На главную</Link>
      </p>
      <h1>Онлайн-запись</h1>
      <BookingWizard />
    </main>
  );
}
