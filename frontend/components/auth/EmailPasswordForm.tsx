import { signIn } from "@/auth";

function EmailPasswordForm() {
    return (
        <form action={
            async (formData) => {
                "use server"

                await signIn('aws-ses', formData)
            }

        } className="flex flex-row gap-4 ">
            <input type="text" className="w-full class" name="email" placeholder="Email" />
            <button type="submit" className="bg-black p-4 px-6 text-white w-40"> Sign In</button>
        </form>
    );
}

export default EmailPasswordForm;