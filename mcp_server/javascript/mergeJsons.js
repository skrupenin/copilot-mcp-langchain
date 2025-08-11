function mergeJsons(parameters) {
    const { json_arrays } = parameters;
    
    if (!Array.isArray(json_arrays)) {
        return [];
    }
    
    // Parse each array if it's a string, or use directly if it's already an array
    const parsedArrays = json_arrays.map(arr => {
        if (typeof arr === 'string') {
            try {
                return JSON.parse(arr);
            } catch (e) {
                return [];
            }
        }
        if (Array.isArray(arr)) {
            return arr;
        }
        if (typeof arr === 'object' && arr !== null) {
            return [arr];
        }
        return [];
    });
    
    // Merge all arrays into one
    const mergedJson = parsedArrays.flat();
    
    // Remove duplicates by date (keep the last occurrence)
    const uniqueJson = [];
    const dates = new Set();
    for (let i = mergedJson.length - 1; i >= 0; i--) {
        if (!dates.has(mergedJson[i].date)) {
            dates.add(mergedJson[i].date);
            uniqueJson.unshift(mergedJson[i]);
        }
    }
    
    // Sort by date
    uniqueJson.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    return uniqueJson;
}