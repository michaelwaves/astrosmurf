import { redirectToCustomerPortal } from "@/lib/stripe/customer_portal";
import { Button } from "../ui/button";
export function ManageSubscriptionButton() {
    return (
        <form action={redirectToCustomerPortal}>
            <Button type="submit">
                Manage Subscription
            </Button>
        </form>
    );
}