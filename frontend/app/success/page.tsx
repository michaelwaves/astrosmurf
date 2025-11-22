import { redirect } from "next/navigation";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)
async function SuccessPage({ searchParams }: {
    searchParams: { session_id?: string }
}) {
    if (!searchParams.session_id) {
        redirect("/")
    }
    const session = await stripe.checkout.sessions.retrieve(searchParams.session_id)

    if (session.payment_status !== 'paid') {
        redirect('/pricing');
    }
    return (
        <div className="max-w-2xl mx-auto p-8">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h1 className="text-2xl font-bold text-green-900 mb-2">
                    🎉 Payment Successful!
                </h1>
                <p className="text-green-800">
                    Thank you for your purchase, {session.customer_details?.email}
                </p>
                <p className="text-sm text-green-700 mt-2">
                    Order ID: {session.id}
                </p>
            </div>

            <div className="mt-6">
                <a href="/d" className="text-blue-600 hover:underline">
                    Go to Dashboard →
                </a>
            </div>
        </div>
    );
}

export default SuccessPage;