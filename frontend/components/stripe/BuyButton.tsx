import { createCheckoutSession } from "@/lib/stripe/checkout";
import { Button } from "../ui/button";

function BuyButton({ priceId, label = "Buy Now" }: { priceId: string, label?: string }) {
    return (
        <form action={createCheckoutSession.bind(null, priceId)}>
            <Button
                type="submit">
                {label}
            </Button>
        </form>
    );
}

export default BuyButton;