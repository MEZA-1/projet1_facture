    $(document).on('click','#btn-add', function(){
        var number = $('#wrapper').children().length +1;

        let formAdd = `<div class="form-row">
            <div class="form-group col-md-3">
                <label for="product-${number}">#${number} Product</label>
                <select required name="product" class="form-control" id="product-${number}">
                    <option value="">Choose a product ...</option>
                    {% for product in products %}
                    <option value="{{ product.id }}" data-price="{{ product.unit_price }}">{{ product.name }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group col-md-3">
                <label for="qty-${number}">Quantity</label>
                <input required name="qty" type="number" min="1" step="1" class="form-control" id="qty-${number}">
            </div>

            <div class="form-group col-md-3">
                <label for="unit_price-${number}">Unit price</label>
                <input required name="unit_price" type="number" min="0" readonly step="0.01" class="form-control" id="unit_price-${number}">
            </div>

            <div class="form-group col-md-3">
                <label for="total_article-${number}">Total Article</label>
                <input required name="total_article" type="number" min="0" readonly step="0.01" class="form-control" id="total_article-${number}">
            </div>
            
            `;

        $("#wrapper:last").append(formAdd);
    })

    function recalcLine(number) {
        const productSelect = $(`#product-${number}`);
        const qtyInput = $(`#qty-${number}`);
        const unitPriceInput = $(`#unit_price-${number}`);
        const totalArticleInput = $(`#total_article-${number}`);

        if (!productSelect.length || !qtyInput.length) {
            return;
        }

        const price = parseFloat(productSelect.find(":selected").data("price")) || 0;
        const qty = parseFloat(qtyInput.val()) || 0;
        const total = price * qty;

        unitPriceInput.val(price ? price.toFixed(2) : "");
        totalArticleInput.val(total ? total.toFixed(2) : "");
        recalcInvoiceTotal();
    }

    function recalcInvoiceTotal() {
        let total = 0;
        $("[id^='total_article-']").each(function () {
            const value = parseFloat($(this).val());
            if (!isNaN(value)) {
                total += value;
            }
        });
        $("#total_invoice").val(total ? total.toFixed(2) : "");
    }

    $(document).on('change', "select[id^='product-']", function () {
        const number = $(this).attr("id").split("-")[1];
        recalcLine(number);
    });

    $(document).on('input', "input[id^='qty-']", function () {
        const number = $(this).attr("id").split("-")[1];
        recalcLine(number);
    });

    $(document).on('click','#btn-remove', function () {
        $("#wrapper").children().last().remove();
        recalcInvoiceTotal();
    })