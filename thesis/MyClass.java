public class MyClass
{
	public int MyMethod(int a, int b)
	{
		while (a != b)
		{
			if (a < b)
				b -= a;
			else
				a -= b;
		}
	}
}
