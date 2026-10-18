/**
 * Picks and orders the links of a collection. The chosen ids are submitted as links[] in the
 * order shown, which is the order visitors see. Buttons reorder, so no dragging is needed.
 */
export default function linkList(config) {
    const catalogue = new Map(config.all.map((link) => [link.id, link]));

    return {
        chosen: [...(config.chosen ?? [])],
        picking: '',

        get items() {
            return this.chosen.map((id) => catalogue.get(id)).filter(Boolean);
        },

        get available() {
            return config.all.filter((link) => !this.chosen.includes(link.id));
        },

        get hasItems() {
            return this.chosen.length > 0;
        },

        get hasAvailable() {
            return this.available.length > 0;
        },

        isFirst(index) {
            return index === 0;
        },

        isLast(index) {
            return index === this.chosen.length - 1;
        },

        add() {
            const id = Number(this.picking);

            if (id && !this.chosen.includes(id)) {
                this.chosen.push(id);
            }

            this.picking = '';
        },

        remove(index) {
            this.chosen.splice(index, 1);
        },

        move(index, step) {
            const target = index + step;

            if (target < 0 || target >= this.chosen.length) {
                return;
            }

            const [moved] = this.chosen.splice(index, 1);
            this.chosen.splice(target, 0, moved);
        },

        label(template, link) {
            return template.replace(':title', link.title);
        },
    };
}
