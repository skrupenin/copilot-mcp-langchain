function mergeJsons(parameters) {
    let { json_arrays } = parameters;
    
    // If json_arrays is a string, try to parse it as JSON first
    if (typeof json_arrays === 'string') {
        try {
            json_arrays = JSON.parse(json_arrays);
        } catch (e) {
            return [];
        }
    }
    
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
        // If it's already an array or object, use it directly
        if (Array.isArray(arr)) {
            return arr;
        }
        // If it's a single object, wrap it in an array
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