"use server"

import { signOut } from "@/auth"
const signOutServer = async () => {
    await signOut({ redirectTo: "/" })

}

export { signOutServer }