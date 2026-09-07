namespace MemoryMap;

/// <summary>
/// Feature flags for the diagnosability exercise (see top-level README).
/// Each flag below introduces exactly one deliberate bug into <see cref="MemoryPage"/>.
/// Flip a single flag to <c>true</c> to enable that bug and see its effect on the
/// test suite; leave every flag <c>false</c> for a correct implementation. Enable
/// at most one flag at a time.
/// Do not read MemoryPage.cs to find out what a flag does before you've written
/// your bug report from the test failures alone - that's the point of the exercise!
/// </summary>
public static class BugFlags
{
    public static readonly bool Bug1 = false;
    public static readonly bool Bug2 = false;
    public static readonly bool Bug3 = false;
    public static readonly bool Bug4 = false;
    public static readonly bool Bug5 = false;
    public static readonly bool Bug6 = false;
    public static readonly bool Bug7 = false;
    public static readonly bool Bug8 = false;
    public static readonly bool Bug9 = false;
    public static readonly bool Bug10 = false;
    public static readonly bool Bug11 = false;
    public static readonly bool Bug12 = false;
}
