const searchRoot = document.querySelector("[data-search-root]");

if (searchRoot) {
    const input = document.getElementById("site-search-input");
    const clearButton = searchRoot.querySelector("[data-search-clear]");
    const resultsWrap = searchRoot.querySelector("[data-search-results-wrap]");
    const resultsList = searchRoot.querySelector("[data-search-results]");
    const countLabel = searchRoot.querySelector("[data-search-count]");
    const statusLabel = searchRoot.querySelector("[data-search-status]");
    const emptyState = searchRoot.querySelector("[data-search-empty]");
    const loadingState = searchRoot.querySelector("[data-search-loading]");
    const errorState = searchRoot.querySelector("[data-search-error]");
    const noResultsState = searchRoot.querySelector("[data-search-no-results]");
    const openButtons = document.querySelectorAll("[data-search-open]");
    const closeButtons = searchRoot.querySelectorAll("[data-search-close]");
    const suggestionButtons = searchRoot.querySelectorAll("[data-search-suggestion]");

    const state = {
        ready: false,
        loading: false,
        open: false,
        items: [],
        matches: [],
        activeIndex: -1,
        previousFocus: null,
    };

    const searchPath = searchRoot.dataset.indexUrl;

    const strings = {
        loading: "正在加载搜索索引...",
        ready: "支持标题、摘要、标签和自定义关键词匹配",
        noResults: "没有找到匹配结果，试试缩短关键词。",
        loadError: "搜索索引加载失败，请刷新页面后重试。",
    };

    const escapeHtml = (value) => String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

    const normalize = (value) => String(value || "")
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[`~!@#$%^&*()+=\[\]{}\\|;:'",.<>/?_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();

    const tokenize = (query) => normalize(query)
        .split(" ")
        .filter(Boolean);

    const formatDate = (value) => {
        if (!value) {
            return "";
        }

        return value.slice(0, 10);
    };

    const snippetFor = (item, tokens) => {
        const sources = [item.summary, item.content, item.title].filter(Boolean);
        if (!sources.length) {
            return "";
        }

        const matchedSource = sources.find((source) => tokens.some((token) => source.toLowerCase().includes(token.toLowerCase())));
        const source = matchedSource || sources[0];
        const lowered = source.toLowerCase();
        let matchIndex = -1;

        for (const token of tokens) {
            matchIndex = lowered.indexOf(token.toLowerCase());
            if (matchIndex !== -1) {
                break;
            }
        }

        if (matchIndex === -1 || source.length <= 150) {
            return source;
        }

        const start = Math.max(0, matchIndex - 36);
        const end = Math.min(source.length, start + 150);
        const prefix = start > 0 ? "..." : "";
        const suffix = end < source.length ? "..." : "";
        return `${prefix}${source.slice(start, end).trim()}${suffix}`;
    };

    const renderTags = (values, kind) => {
        if (!values || !values.length) {
            return "";
        }

        return values.slice(0, 4).map((value) => (
            `<span class="site-search-chip site-search-chip-${kind}">${escapeHtml(value)}</span>`
        )).join("");
    };

    const setVisibleState = (name) => {
        emptyState.classList.toggle("hidden", name !== "empty");
        loadingState.classList.toggle("hidden", name !== "loading");
        errorState.classList.toggle("hidden", name !== "error");
        noResultsState.classList.toggle("hidden", name !== "no-results");
        resultsWrap.classList.toggle("hidden", name !== "results");
    };

    const setStatus = (value) => {
        statusLabel.textContent = value;
    };

    const prepareItems = (items) => items.map((item) => {
        const title = item.title || "";
        const summary = item.summary || "";
        const content = item.content || "";
        const tags = Array.isArray(item.tags) ? item.tags : [];
        const categories = Array.isArray(item.categories) ? item.categories : [];
        const keywords = Array.isArray(item.keywords) ? item.keywords : [];
        const titleNorm = normalize(title);
        const summaryNorm = normalize(summary);
        const contentNorm = normalize(content);
        const tagNorm = normalize(tags.join(" "));
        const categoryNorm = normalize(categories.join(" "));
        const keywordNorm = normalize(keywords.join(" "));
        const dateTs = Date.parse(item.date || "") || 0;
        const lastmodTs = Date.parse(item.lastmod || item.date || "") || 0;
        const recencyBoost = Math.max(0, Math.min(40, Math.round((lastmodTs - dateTs) / 86400000)));

        return {
            title,
            permalink: item.permalink || "#",
            summary,
            content,
            tags,
            categories,
            keywords,
            dateLabel: formatDate(item.date),
            lastmodLabel: formatDate(item.lastmod),
            dateTs,
            lastmodTs,
            titleNorm,
            summaryNorm,
            contentNorm,
            tagNorm,
            categoryNorm,
            keywordNorm,
            recencyBoost,
            searchNorm: [titleNorm, summaryNorm, contentNorm, tagNorm, categoryNorm, keywordNorm].join(" ").trim(),
        };
    });

    const scoreItem = (item, normalizedQuery, tokens) => {
        let score = 0;
        let matches = 0;

        if (!normalizedQuery) {
            return null;
        }

        if (item.titleNorm === normalizedQuery) {
            score += 500;
        } else if (item.titleNorm.startsWith(normalizedQuery)) {
            score += 260;
        } else if (item.titleNorm.includes(normalizedQuery)) {
            score += 180;
        }

        if (item.tagNorm.includes(normalizedQuery)) {
            score += 120;
        }

        if (item.categoryNorm.includes(normalizedQuery)) {
            score += 100;
        }

        if (item.summaryNorm.includes(normalizedQuery)) {
            score += 75;
        }

        if (item.contentNorm.includes(normalizedQuery)) {
            score += 50;
        }

        if (item.keywordNorm.includes(normalizedQuery)) {
            score += 60;
        }

        for (const token of tokens) {
            let tokenScore = 0;

            if (item.titleNorm.startsWith(token)) {
                tokenScore += 90;
            } else if (item.titleNorm.includes(token)) {
                tokenScore += 60;
            }

            if (item.tagNorm.includes(token)) {
                tokenScore += 38;
            }

            if (item.categoryNorm.includes(token)) {
                tokenScore += 32;
            }

            if (item.keywordNorm.includes(token)) {
                tokenScore += 28;
            }

            if (item.summaryNorm.includes(token)) {
                tokenScore += 20;
            }

            if (item.contentNorm.includes(token)) {
                tokenScore += 14;
            }

            if (tokenScore > 0) {
                matches += 1;
                score += tokenScore;
            }
        }

        if (tokens.length > 1 && matches === tokens.length) {
            score += 80;
        }

        if (!score) {
            return null;
        }

        return score + item.recencyBoost;
    };

    const rankItems = (query, requireAllTerms) => {
        const normalizedQuery = normalize(query);
        const tokens = tokenize(query);

        return state.items
            .map((item) => {
                if (requireAllTerms && tokens.length > 1) {
                    const containsAll = tokens.every((token) => item.searchNorm.includes(token));
                    if (!containsAll) {
                        return null;
                    }
                }

                const score = scoreItem(item, normalizedQuery, tokens);
                if (!score) {
                    return null;
                }

                return { item, score };
            })
            .filter(Boolean)
            .sort((left, right) => (
                right.score - left.score
                || right.item.lastmodTs - left.item.lastmodTs
                || right.item.dateTs - left.item.dateTs
                || left.item.title.localeCompare(right.item.title)
            ))
            .slice(0, 18);
    };

    const setActiveResult = (index) => {
        const links = resultsList.querySelectorAll(".site-search-result");

        links.forEach((link, currentIndex) => {
            link.classList.toggle("is-active", currentIndex === index);
        });

        state.activeIndex = index;

        if (index >= 0 && links[index]) {
            links[index].focus();
        } else {
            input.focus();
        }
    };

    const renderResults = (matches, query) => {
        const tokens = tokenize(query);

        resultsList.innerHTML = matches.map(({ item }) => {
            const meta = [
                item.lastmodLabel || item.dateLabel,
                item.categories.length ? escapeHtml(item.categories.slice(0, 2).join(" / ")) : "",
                item.tags.length ? escapeHtml(item.tags.slice(0, 3).join(" / ")) : "",
            ].filter(Boolean).map((value) => `<span>${value}</span>`).join("");

            const chips = `${renderTags(item.categories, "category")}${renderTags(item.tags, "tag")}`;
            const summary = escapeHtml(snippetFor(item, tokens));

            return `
                <a class="site-search-result" href="${item.permalink}">
                    <div class="site-search-result-main">
                        <div class="site-search-result-header">
                            <strong>${escapeHtml(item.title)}</strong>
                        </div>
                        ${summary ? `<p>${summary}</p>` : ""}
                        ${chips ? `<div class="site-search-chip-row">${chips}</div>` : ""}
                    </div>
                    ${meta ? `<div class="site-search-result-meta">${meta}</div>` : ""}
                </a>
            `;
        }).join("");

        countLabel.textContent = `${matches.length} 条结果`;
        state.matches = matches;
        setActiveResult(-1);
    };

    const showEmptyState = () => {
        state.matches = [];
        state.activeIndex = -1;
        setVisibleState("empty");
        setStatus(state.ready ? strings.ready : strings.loading);
        clearButton.classList.toggle("hidden", !input.value.trim());
    };

    const runSearch = (query) => {
        const trimmed = query.trim();
        clearButton.classList.toggle("hidden", !trimmed);

        if (!trimmed) {
            showEmptyState();
            return;
        }

        if (!state.ready) {
            setVisibleState("loading");
            setStatus(strings.loading);
            return;
        }

        let matches = rankItems(trimmed, true);
        if (!matches.length) {
            matches = rankItems(trimmed, false);
        }

        if (!matches.length) {
            state.matches = [];
            setVisibleState("no-results");
            setStatus(strings.noResults);
            return;
        }

        renderResults(matches, trimmed);
        setVisibleState("results");
        setStatus(`找到 ${matches.length} 条与“${trimmed}”相关的结果`);
    };

    const debounce = (fn, wait) => {
        let timer = null;
        return (...args) => {
            window.clearTimeout(timer);
            timer = window.setTimeout(() => fn(...args), wait);
        };
    };

    const handleInput = debounce(() => {
        runSearch(input.value);
    }, 80);

    const loadIndex = async () => {
        if (state.ready || state.loading) {
            return;
        }

        state.loading = true;
        setVisibleState("loading");
        setStatus(strings.loading);

        try {
            const response = await fetch(searchPath, { credentials: "same-origin" });
            if (!response.ok) {
                throw new Error(`Failed to load search index: ${response.status}`);
            }

            const rawItems = await response.json();
            state.items = prepareItems(rawItems);
            state.ready = true;
            state.loading = false;
            showEmptyState();
        } catch (error) {
            console.error(error);
            state.loading = false;
            setVisibleState("error");
            setStatus(strings.loadError);
        }
    };

    const openSearch = async (seed = "") => {
        if (state.open) {
            if (seed) {
                input.value = seed;
                runSearch(seed);
            }
            input.focus();
            input.select();
            return;
        }

        state.previousFocus = document.activeElement;
        state.open = true;
        searchRoot.hidden = false;
        document.body.classList.add("search-modal-open");

        if (!state.ready) {
            await loadIndex();
        } else {
            showEmptyState();
        }

        if (seed) {
            input.value = seed;
            runSearch(seed);
        }

        window.setTimeout(() => {
            input.focus();
            input.select();
        }, 30);
    };

    const closeSearch = () => {
        if (!state.open) {
            return;
        }

        state.open = false;
        searchRoot.hidden = true;
        document.body.classList.remove("search-modal-open");
        input.value = "";
        showEmptyState();

        if (state.previousFocus && typeof state.previousFocus.focus === "function") {
            state.previousFocus.focus();
        }
    };

    openButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            openSearch();
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            closeSearch();
        });
    });

    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const query = button.dataset.searchSuggestion || button.textContent || "";
            openSearch(query);
        });
    });

    clearButton.addEventListener("click", () => {
        input.value = "";
        showEmptyState();
        input.focus();
    });

    input.addEventListener("input", handleInput);

    input.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown") {
            if (!state.matches.length) {
                return;
            }

            event.preventDefault();
            const nextIndex = Math.min(state.activeIndex + 1, state.matches.length - 1);
            setActiveResult(nextIndex);
            return;
        }

        if (event.key === "ArrowUp") {
            if (!state.matches.length) {
                return;
            }

            event.preventDefault();
            const nextIndex = state.activeIndex <= 0 ? -1 : state.activeIndex - 1;
            setActiveResult(nextIndex);
            return;
        }

        if (event.key === "Enter" && state.matches.length) {
            const nextIndex = state.activeIndex >= 0 ? state.activeIndex : 0;
            const links = resultsList.querySelectorAll(".site-search-result");
            if (links[nextIndex]) {
                links[nextIndex].click();
            }
        }
    });

    resultsList.addEventListener("mousemove", (event) => {
        const link = event.target.closest(".site-search-result");
        if (!link) {
            return;
        }

        const links = Array.from(resultsList.querySelectorAll(".site-search-result"));
        const nextIndex = links.indexOf(link);
        if (nextIndex !== -1 && nextIndex !== state.activeIndex) {
            setActiveResult(nextIndex);
        }
    });

    document.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
            event.preventDefault();

            if (state.open) {
                closeSearch();
            } else {
                openSearch();
            }
            return;
        }

        if (event.key === "Escape" && state.open) {
            event.preventDefault();
            closeSearch();
        }
    });

    showEmptyState();
}
