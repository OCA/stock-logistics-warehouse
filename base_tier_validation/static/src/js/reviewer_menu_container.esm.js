/** @odoo-module **/

// ensure components are registered beforehand.
import {getMessagingComponent} from "@mail/utils/messaging_component";

const {Component} = owl;

export class ReviewerMenuContainer extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.env.services.messaging.modelManager.messagingCreatedPromise.then(() => {
            this.reviewerMenuView =
                this.env.services.messaging.modelManager.messaging.models.ReviewerMenuView.insert();
            this.render();
        });
    }
}

Object.assign(ReviewerMenuContainer, {
    components: {ReviewerMenuView: getMessagingComponent("ReviewerMenuView")},
    template: "base_tier_validation.ReviewerMenuContainer",
});
