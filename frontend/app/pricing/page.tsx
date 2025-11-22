import BuyButton from "@/components/stripe/BuyButton";
import { ManageSubscriptionButton } from "@/components/stripe/ManageSubscriptionButton";
import SubscribeButton from "@/components/stripe/SubscribeButton";

function PricingPage() {
    return (
        <div>
            <h1>Buy MCP API credits</h1>
            <p>$5 / 1000 credits</p>
            <BuyButton priceId="price_1SIvBJ2MPHDLQn3OHLUW91td" label="One Time Payment" />
            <SubscribeButton
                priceId="price_1SJIve2MPHDLQn3OA9ivnWq1"
                label="Subscribe" />
            <ManageSubscriptionButton />
        </div>
    );
}

export default PricingPage;