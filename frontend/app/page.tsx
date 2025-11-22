import { auth } from "@/auth";
import SignInButtons from "@/components/auth/SignInButtons";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await auth()
  if (session?.user) {
    redirect("/d")
  }
  return (
    <div>
      <SignInButtons />
    </div>
  );
}
