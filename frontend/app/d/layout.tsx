import { auth } from "@/auth";
import { redirect } from "next/navigation";
import React from "react";

async function DashboardLayoutPage({ children }: { children: React.ReactNode }) {
    const session = await auth()
    if (!session?.user) {
        redirect("/")
    }
    return (
        <div>
            {children}
        </div>
    );
}

export default DashboardLayoutPage;