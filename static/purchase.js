

    function initiatePurchase(event) {
        event.preventDefault();
        let purchaseData = new FormData();
        purchaseData.append({"test":"test"});


        // fetch({{ url_for('make_purchase') }}, {
        fetch('/make-purchase', {
            "method": "POST",
            "body": purchaseData
        }).then((response) => {

            console.log(response);
            return false;

        });

    }