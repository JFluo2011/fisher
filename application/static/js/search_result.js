class Pagination {
    constructor() {
        self.that = this
    }

    onPageClick(event, page) {
        window.location.href = $SCRIPT_ROOT + '/book/search?keyword=' + self.that.keyword + '&page=' + page
    }

    pagination(total, visbleCount, startPage) {
        $('#pagination').twbsPagination({
            initiateStartPageClick: false,
            hideOnlyOnePage: false,
            startPage: startPage,
            totalPages: total,
            visiblePages: visbleCount,
            onPageClick: self.that.onPageClick,
            first: '首页',
            last: '尾页',
            next:'后页>',
            prev:'<前页'
        })
    }

    initForSearch() {
        let page = getQueryString('page');
        if (!page) {
            page = 1
        }
        else{
            page = parseInt(page)
        }
        self.that.keyword = $('#keyword').text();
        let total = $('#total').text();
        total = Math.floor(parseInt(total) / 10) + 1;
        self.that.pagination(total, 6, page)
    }
}

new Pagination().initForSearch();

