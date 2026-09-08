using MemoryMap;

namespace MemoryMapTests;

public class MemoryPageApprovalTests
{
        
    // Example test using basic printer and simpler scenario builder
    [Test]
    public Task BasicReadmeScenario()
    {
        var scenario = new BasicScenario(sizeBytes: 8);
        
        scenario.Allocate("A", MemoryUnit.DWord);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Deallocate("A");
        scenario.Allocate("C", MemoryUnit.Word);

        return Verify(scenario.Text());
    }
    
    // Example Test with more sophisticated printer and scenario builder
    [Test]
    public Task ReadmeScenario()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Describe(
            "This is the example scenario from the kata README: allocate a DWord, " +
            "allocate a Byte, deallocate the DWord, then allocate a Word. Each " +
            "allocation should land exactly where the README diagram shows.");

        scenario.Allocate("A", MemoryUnit.DWord);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Deallocate("A");
        scenario.Allocate("C", MemoryUnit.Word);

        return Verify(scenario.Text());
    }
}
