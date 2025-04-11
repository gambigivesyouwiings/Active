    // Modified initialization function
    function initImageSortable() {
        const container = $('#image-preview-container');
        let maxScroll = 0;
        let isDragging = false;

        // Destroy previous sortable instance
        if (container.sortable('instance')) {
            container.sortable('destroy');
        }

        // Initialize new sortable
        container.sortable({
            items: '.draggable-image',
            cursor: 'grabbing',
            axis: 'x',
            containment: 'parent',
            scroll: false,
            delay: 50,
            tolerance: 'pointer',
            helper: function(e, ui) {
                // Preserve original dimensions during drag
                return ui.clone().css({
                    width: ui.outerWidth(),
                    height: ui.outerHeight(),
                    pointerEvents: 'none'
                });
            },
            start: function(e, ui) {
                isDragging = true;
                container.addClass('dragging');
                maxScroll = container[0].scrollWidth - container.width();
                ui.helper.css({
                    zIndex: 1000,
                    transform: 'scale(1.02)'
                });
            },
            stop: function(e, ui) {
                isDragging = false;
                container.removeClass('dragging');
                htmx.trigger(container[0], 'request');
            },
            sort: function(e, ui) {
                if (!isDragging) return;

                const sensitivity = 50;
                const scrollSpeed = 30;
                const currentScroll = container.scrollLeft();
                const mouseX = e.pageX - container.offset().left;

                // Left edge scroll
                if (mouseX < sensitivity) {
                    const newScroll = Math.max(0, currentScroll - scrollSpeed);
                    container.scrollLeft(newScroll);
                }
                // Right edge scroll
                else if (mouseX > container.width() - sensitivity) {
                    const newScroll = Math.min(maxScroll, currentScroll + scrollSpeed);
                    container.scrollLeft(newScroll);
                }

                // Update scroll shadows
                container.toggleClass('can-scroll-left', currentScroll > 0);
                container.toggleClass('can-scroll-right', currentScroll < maxScroll);
            }
        });

        // Scroll shadow logic
        container.on('scroll', function() {
            if (!isDragging) {
                const currentScroll = container.scrollLeft();
                container.toggleClass('can-scroll-left', currentScroll > 0);
                container.toggleClass('can-scroll-right', currentScroll < maxScroll);
            }
        });

        // Reinitialize scroll shadows
        setTimeout(() => {
            maxScroll = container[0].scrollWidth - container.width();
            container.toggleClass('can-scroll-right', maxScroll > 0);
        }, 100);
    }

    // Initialize on page load
    $(document).ready(initImageSortable);

    // Reinitialize after HTMX updates
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.target.id === 'image-preview-container') {
            initImageSortable();
        }
    });

    // Handle image loading
    document.body.addEventListener('htmx:afterProcessNode', function(evt) {
        const images = evt.detail.elt.querySelectorAll('.draggable-image img');
        images.forEach(img => {
            img.onload = function() {
                this.style.opacity = '1';
            };
            if (img.complete) img.style.opacity = '1';
        });
    });
