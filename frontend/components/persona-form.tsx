"use client"

import { Input } from "./ui/input";
import { useForm } from "react-hook-form"

function PersonaForm() {
    const form = useForm({
        defaultValues: {
            name: "",
            description: "",
            image_url: ""
        }
    })
    return (
        <form>
            <Input {...form.register("name")} />
            <Input {...form.register("description")} />
            <Input type="file" />

        </form>
    );
}

export default PersonaForm;