using MemoryMap;

namespace MemoryMapTests;

internal static class TypeNames
{
    public static readonly IReadOnlyDictionary<int, string> ById = new Dictionary<int, string>
    {
        [MemoryUnit.Bool] = "Bool",
        [MemoryUnit.Byte] = "Byte",
        [MemoryUnit.Word] = "Word",
        [MemoryUnit.DWord] = "DWord",
    };
}

internal static class MemoryPagePrinter
{
    public static string Print(MemoryPage memory)
    {
        var sizeBytes = memory.SizeBits / 8;
        var bytesHeader = "|" + string.Concat(Enumerable.Range(0, sizeBytes).Select(b => $"{b,-9}")) + "|  Bytes";
        var bitsHeader = "|" + string.Concat(Enumerable.Repeat("01234567 ", sizeBytes)) + "|  Bits";

        var usage = Enumerable.Repeat('-', memory.SizeBits).ToArray();
        foreach (var allocation in memory.Allocations)
        {
            var idChar = allocation.Id[^1];
            usage[allocation.StartBit] = char.ToUpperInvariant(idChar);
            for (var bit = allocation.StartBit + 1; bit < allocation.StartBit + allocation.SizeBits; bit++)
            {
                usage[bit] = char.ToLowerInvariant(idChar);
            }
        }

        var usageBytes = Enumerable.Range(0, sizeBytes)
            .Select(b => new string(usage, b * 8, 8));
        var usageLine = "|" + string.Join(" ", usageBytes) + " |  Memory usage";

        return string.Join("\n", [bytesHeader, bitsHeader, usageLine]);
    }
}

internal sealed class Scenario
{
    private readonly MemoryPage _memory;
    private readonly List<string> _story = [];
    private bool _narrating;

    public Scenario(int sizeBytes)
    {
        _memory = new MemoryPage(sizeBytes);
    }

    public void Describe(string text)
    {
        _narrating = true;
        _story.Add(text);
        var sizeBytes = _memory.SizeBits / 8;
        Show(_memory.Allocations.Count > 0
            ? $"Starting point with maximum {sizeBytes} Bytes:"
            : $"Empty memory page of maximum {sizeBytes} Bytes:");
    }

    public void Allocate(string name, int type)
    {
        Exception? error = null;
        try
        {
            _memory.Allocate(name, type);
        }
        catch (Exception caught)
        {
            if (!_narrating)
            {
                throw;
            }

            error = caught;
        }

        Show($"Allocate {name} of type {TypeNames.ById[type]}");
        ReportError(error);
    }

    public void Deallocate(string name)
    {
        Exception? error = null;
        try
        {
            _memory.Deallocate(name);
        }
        catch (Exception caught)
        {
            if (!_narrating)
            {
                throw;
            }

            error = caught;
        }

        Show($"Deallocate {name}");
        ReportError(error);
    }

    public string Text() => string.Join("\n", _story);

    private void Separate()
    {
        if (_story.Count > 0 && _story[^1] != "")
        {
            _story.Add("");
        }
    }

    private void Show(string label)
    {
        if (!_narrating)
        {
            return;
        }

        Separate();
        _story.Add(label);
        _story.Add(MemoryPagePrinter.Print(_memory));
    }

    private void ReportError(Exception? error)
    {
        if (_narrating && error is not null)
        {
            _story.Add($"{error.GetType().Name}: {error.Message}");
        }
    }
}
